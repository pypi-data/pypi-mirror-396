    Title: Taurus Startup and Polling Performance Optimization
    TEP: 21
    State: ACCEPTED
    Date: 2023
    Drivers: ALBA Synchrotron
    URL: http://www.taurus-scada.org/tep/?TEP21.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
      Taurus GUIs managing hundreds of attributes may suffer from long startup times and fragile polling, especially in the presence of slow or timeout-prone attributes. TEP21 defines a plan to optimize Taurus startup and polling performance by fixing core inefficiencies, introducing systematic benchmarking and improving event subscription strategies.

## Motivation

Taurus-based GUIs at accelerators and beamlines frequently manage hundreds of Tango attributes, many of them event-driven. Users have long reported slow startup times (20–30 s for typical control room applications), fragile polling performance and poor responsiveness in the presence of slow, timeout-prone or event-flooding attributes.
Improving Taurus startup time and attribute subscription robustness would directly benefit all Taurus deployments, including large-scale GUIs at several facilities.

This proposal describes a set of improvements collectively known as *Taurus Performance Optimization (TPO)*. The work started in 2023 and includes work directly in Taurus and additional work that will need to be coordinated with Tango Core.

## Background

Profiling and benchmarking work developed at the beginning of TPO identified several bottlenecks:

- Unnecessary repetitive calls (`getElementAlias()`, `fqdn_no_alias()`).
- Triple reads for attributes without events and double reads for attributes with events under specific conditions (ATTR_CONF_EVENT + polling expirations).
- Polling thread creation bugs (thread created too early, entering sleep without work).
- Synchronous read performed inside `DeviceProxy.subscribe_event()`, which can block up to 3 s per attribute in case of slow or timeout attributes.

Benchmarking (fast/slow/timeout/exception attributes) demonstrated that Taurus startup can be significantly improved and that it does not scale well with increasing numbers of attributes, especially those with events.

## Goals

The objective of TEP21 is to address Taurus inefficiencies regarding the slow start of GUIs, and to improve the polling and event subscription mechanisms, providing:

- Fast and scalable GUI startup.
- Robust handling of slow, timeout and missing attributes during initialization.
- A mechanism to guarantee that all attributes have an initial value within a reasonable time (e.g. within one polling cycle for attributes without events).
- Clear benchmark coverage to avoid regressions.

## Proposed Design and Roadmap

The project will be divided into two phases, Taurus Core Optimizations (TPO1) and event subscription improvements (TPO2).

### Core Taurus Optimizations (TPO1)

- Removal of redundant method calls.
- Fixes to polling thread lifecycle.
- Improved read cache behavior.
- Avoid reads during startup when subscription fails.
- Addition of benchmark tests to measure startup times and detect regressions.

### Event Subscription Improvements (TPO2)

The main design motivation is avoiding the synchronous read performed by Tango during event subscription. Three approaches will be evaluated:

#### Option A: Internal Taurus Async Subscriber (Delayed/AsyncSubscriber)

Implement (or improve the existing `DelayedSubscriber` to be easier to use) a new background thread (we'll call it "subscribe thread" from now on) that will try to subscribe to change events in background.

Currently, Taurus tries to subscribe to change events as soon as `setModel` is called. With the new approach:

- The `setModel` will not immediately subscribe to change events. Instead, it will enable polling for all attributes as if the attribute doesn't send events.
- Once the application is open, the subscribe thread will attempt to subscribe to events for all attributes.
  - If an attribute does not send events, it will remain in polling mode and will be removed from the subscribe thread.
  - If an attribute does send events, the thread will successfully subscribe. Then it will be removed from the subscribe thread and also from the polling thread.

**Pros:**

- No Tango changes required.

**Cons:**

- While this approach is functional, it's not ideal. It will take some time to try to subscribe to events for all attributes. So if an attribute is sending events every 0.5 s, it will be updated every 3 s (or the polling period set) until this subscribe thread subscribes to that specific attribute.

#### Option B: Tango Event Subscription without Read

Add a new argument to Tango `subscribe_event()` method, called `read_attr` (or alternatively `avoid_read`, `read_value`, etc.). By default, this argument will be set to `True`, preserving the current behavior. When set to `False`, `subscribe_event()` will return immediately with the event ID or raise an exception if the attribute doesn’t send events. Unlike the current behavior, it won’t trigger a `push_event` callback since no read is performed.

In this scenario, it becomes the caller’s responsibility to retrieve the attribute value through other methods.

Taurus logic:

1. Attribute added temporarily to polling with a one-shot flag.
2. Polling retrieves first value (≤ 3 s guaranteed).
3. Attribute removed from polling once events start.

For most attributes, this polling workflow won’t be necessary because the attribute would typically send an event within a few seconds. However, we want to ensure that every attribute will have a value within 3 seconds or less, even if the attribute only sends events infrequently (e.g., once a day).

**Pros:**

- Small Tango-side modification.
- Good startup behavior.

**Cons:**

- Requires more work on the Taurus side.

#### Option C: Tango asynchronous event subscription

We propose a new `subscribe_event_asynch()` method, similar to `read_attributes_asynch()`. This method would return immediately with the event ID but perform the actual read asynchronously. Once the value is retrieved, it would trigger the `push_event` callback as usual.

In Taurus, this would work as follows:

1. `subscribe_event_asynch()` is called (attributes without events will still raise an exception).
2. When the application opens, most attributes will already have a value.
3. Within a maximum of 3 seconds, all attributes will have a value, even in the worst case (when the last subscribed attribute raises a timeout error, which will call the callback ~3 seconds after the application starts).

**Pros:**

- Best performance and scalability.
- Clean Taurus implementation.
- Guarantees fast startup and early availability of values.

**Cons:**

- Implementation effort on Tango core side.

## Risks

- behavior differences between devices with and without events.
- Tango feature implementation delays.
- Coordination for PyTango bindings.
- Potential performance regressions if benchmark tests are not maintained and run regularly.
