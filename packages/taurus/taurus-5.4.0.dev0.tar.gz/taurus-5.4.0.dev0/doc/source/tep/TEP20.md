    Title: multi-models API
    TEP: 20
    State: ACCEPTED
    Date: 2022-02-09
    Drivers: Carlos Pascual-Izarra cpascual@cells.es
    URL: http://www.taurus-scada.org/tep/?TEP20.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
     Implement support for multiple models in taurus.qt.qtgui.base.

## Intro

`TaurusBaseComponent` and derived classes implement a model API (`setModel`,
`getModelObj`, ...). This API allows Taurus objects (via composition with a Qt
class) to be associated with a *single* `TaurusModel` object to act as their
data source.

The assumption of a single model works for most cases, but it is too limited in
the following two typical use cases which we will refer to as  *"model
containers"* and *"model composers"*:

- The "model container" use case refers to widgets/objects (e.g. `TaurusForm`,
  `TaurusPlot`, ...) that can display an arbitrary number of models. The number
  of models can even vary dynamically, and their order may be relevant.
- The "model composer" widgets/objects differ from the containers in that they
  require a well-defined set of models, each providing the data for a specific
  aspect required by the composer object. One example is
  the `TaurusPlotDataItem`, which requires a model for "X" data and an
  independent model for "Y" data).

This TEP proposes a backwards-compatible implementation to extend the current
API to support the above two use cases.

### Current situation

Appendix I lists the current members of `TaurusBaseComponent` which implicitly
assume a single model. Various custom workarounds are currently implemented by
some classes to bypass the single model limitation imposed by the current
implementation:

- the existing "model container" type widgets (`TaurusForm`
  , `TaurusPlot`, ...) currently reimplement `setModel` (and/or similar methods)
  to accept a sequence of model names and then, instead of actually using the
  rest of the model API ( e.g. registering themselves as listeners), they
  delegate each item of the sequence to a corresponding item class. Usually,
  these model container classes also provide some extended model API (
  e.g. `addModel()`, `insertModel`, `updateModels`, ...) and even slice notation
  support to access the delegate item classes.

- The `TaurusPlotDataItem` is a "model composer" example. It uses the standard
  model API for the "Y" model and complements it with `setXModel`
  and `getXModelName` methods which access a custom `xModel` member of the class
  that keeps a reference to a `TaurusAttribute` to which
  the `TaurusPlotDataItem` is registered as a listener.

- Some widgets such as the `PoolMotorTV` or `TaurusDevicePanel` could also be
  considered "model composers" in that they internally connect to various
  different `TaurusAttributes`. In this case, by accepting the limitation that
  all the attributes are children of the same `TaurusDevice`, the widget can
  reimplement its `setModel` method to accept a device name and then internally
  compose the various required attribute names based on the given device name.

- The `TaurusLabel` widget is currently a single-model widget, but it has been
  proposed that it should be reimplemented to be able to assign independent
  models to its foreground and background.

### Goals

The multi-model support implementation should:

1. be backwards-compatible with existing code
2. support both the "model container" and "model composer" use cases

## Proposed implementation

This is a description of the proposed implementation. Other implementations
were also considered and are briefly mentioned in Appendix III for the record. 

This TEP proposes to support multi-models by assigning a "key" to each model,
replacing the current attributes that imply a single model (e.g., `.modelObj`)
with dictionaries that map those keys to the corresponding values, and adding an
optional `key` keyword argument to the methods that access those attributes (
e.g., `setModel`).

The backwards-compatibility is preserved by making the `key` kwarg optional and
ensuring that the original behaviour is preserved when `key` is not explicitly
passed.

In order to define which model keys are supported by a given object, a new
attribute (e.g. `.modelKeys`) is proposed which would contain a list of valid
keys, the first of which will be used as the default value for `key` when it is
not explicitly provided. In the default implementation, this can have the
value `[""]`.

Also, additional methods are proposed (e.g. `setModels` and `getModelObjs`) that
allow the caller to work directly with dictionaries).

For example one could interact with a multi-model implementation
of `TaurusLabel` as follows:

```python
w = NewTaurusLabel()
w.setModel("tango:sys/tg_test/1/float_scalar")
w.setModel("tango:sys/tg_test/1/state", key="bg")
w.getModelObj()
# -> TangoAttribute(tango://db:10000/sys/tg_test/1/float_scalar)
w.getModelObj(key="")
# -> TangoAttribute(tango://db:10000/sys/tg_test/1/float_scalar)
w.getModelObj(key="bg")
# -> TangoAttribute(tango://db:10000/sys/tg_test/1/state)
w.getModelNames()
# -> {"": "tango:sys/tg_test/1/float_scalar", "bg": "tango:sys/tg_test/1/state"}
```

In order to support the "model container" type of objects, it is proposed that
using `setModel` with a sequence of model names as its first argument and the
special value of `key=MLIST` results in setting each model in the sequence, 
associating it to a dynamically-generated key of the type `(MLIST, i)` where 
`i` is the index of the given model within the sequence. Also note that model 
container widgets may typically define `.modelKeys=[MLIST]` to make this their 
default behaviour. For example one could interact with a multi-model 
implementation of `TaurusForm` as follows:

```python
w = NewTaurusForm()
print(w.modelKeys)
# -> [MLIST]
w.setModel(["eval:'foo'", "eval:'bar'"])
print(w.modelKeys)
# -> [MLIST, (MLIST, 0), (MLIST, 1)]
w.getModelNames()
# -> {MLIST: ("eval:'foo'", "eval:'bar'"), (MLIST, 0): "eval:'foo'", (MLIST, 1): "eval:'bar'"}
w.getModelName(key=w.MLIST)
# -> ("eval:'foo'", "eval:'bar'")
w.getModelName()
# -> ("eval:'foo'", "eval:'bar'")
w.getModelName(key=(w.MLIST,1))
# -> "eval:'bar'"
w.setModel([])
print(w.modelKeys)
# -> [MLIST]
```

### Comments on backwards compatibility implications for taurus users

How does this change affect user-implemented classes?

TLDR; all should work as expected but you may get deprecation warnings if 
you reimplemented a member which in TEP20 requires the `key` kwarg 

Details:

In principle, the changes in the taurus classes proposed here should 
be transparent for user-defined classes that assume the current 
single-model implementation. 

One tricky case is when the existing user-defined class reimplements 
a member which in TEP20 is internally called with the `key` kwarg by our 
base classes. For example, consider the following:

```
class W(Qt.QWidget, TaurusBaseComponent):
    def getModelClass(self):
        return TaurusElementType.Attribute
```

In this case, setting the model via the inherited `AttrWidget.setModel` 
would execute the following call stack (simplified for readability): 

```
W.setModel(m) -> TaurusBaseComponent.setModelName(m, key="") -> W.getModelObject(key="")
```

... which would raise an exception.

This situation should be properly addressed in the TEP20 implementation 
by:
 - handling/avoiding said exception and falling back to a call without the `key` 
kwarg 
 - yielding a deprecation warning to help the user to update their code.

Note that not all the model-related members are actually being internally 
called with the `key` kwarg. Those which are, are listed in Appendix II

### Deprecated members

While not strictly required by the multi-model support, TEP20 tries to 
simplify the model-related public interface by deprecating some currently 
public members (and moving the implementation to private methods).
The deprecated API is:

- `findModelClass`
- `setModelCheck`
- `setModelName`
- `getParentModelName`
- `getParentModelObj`
- `getParentTaurusComponent`
- `getUseParentModel`
- `resetUseParentModel`
- `setUseParentModel`

Note: the `*Parent*` models were already deprecated since taurus 4.3.2, but
now they have been moved to a private implementation while the deprecated 
public method now issues a warning when called.

## Links to more details and discussions

Discussions for this TEP (and the proposed implementation) are conducted in its
associated Pull Request:

https://gitlab.com/taurus-org/taurus/-/merge_requests/1218


## Appendix I - members that implicitly assume single-model 

This is a list of members of the `TaurusBaseComponent` class (and 
`TaurusBaseComponent`-derived subclasses implemented in taurus) that implicitly 
assume a single model:

### TaurusBaseComponent

- Attributes:
    - `_attached`
    - `_localModelName`
    - `_modelInConfig`
    - `_useParentModel`
    - `modelFragmentName`
    - `modelName`
    - `modelObj`

- Methods:
    - `_attach`
    - `_detach`
    - `_findAbsoluteModelClass`
    - `_findRelativeModelClass`
    - `findModelClass`
    - `getDisplayValue`
    - `getFullModelName`
    - `getModel`
    - `getModelClass`
    - `getModelFragmentObj`
    - `getModelInConfig`
    - `getModelIndexValue`
    - `getModelName`
    - `getModelObj`
    - `getModelType`
    - `getModelValueObj`
    - `getParentModelName`
    - `getParentModelObj`
    - `getParentTaurusComponent`
    - `getUseParentModel`
    - `isAttached`
    - `postAttach`
    - `postDetach`
    - `preAttach`
    - `preDetach`
    - `resetModel`
    - `resetModelInConfig`
    - `resetUseParentModel`
    - `setModel`
    - `setModelCheck`
    - `setModelInConfig`
    - `setModelName`
    - `setUseParentModel`

### TaurusBaseWidget

It reimplements some of the above and additionally:

- signals
    - `modelChanged`

- Methods
    - `parentModelChanged`

### TaurusBaseWritableWidget

(nothing apart from reimplementations of some of the above)

### Other `TaurusBaseComponent`-derived classes

Some classes outside `taurus.qt.qtgui.base` reimplement one or more of 
the above (e.g, `TaurusLabel` reimplements `setModel`) but, unless one 
wants to add TEP20 multi-model support to them, no changes are required 
since the `taurus.qt.qtgui.base` classes should provide backwards 
compatibility for the current single-model behaviour.

This is also true for 3rd-party / user-defined classes (e.g. those in 
`taurus_pyqtgraph`)


## Appendix II

This is a list of methods which, if reimplemented in user-defined classes
without support for a `key` kwarg, may trigger deprecation warnings after TEP20
(note that to avoid the warning they may simply accept the `key` kwarg and 
ignore it):

- `getModelClass`
- `getModelFragmentObj`
- `getModelObj`
- `postAttach`
- `postDetach`
- `preAttach`
- `preDetach`
- `setModelCheck`
- `setModelName`



## Appendix III - Alternative implementations

The following implementations were considered (and discarded)

### decorator-based implementation

This was the first approach considered. In this approach, the current pattern of
creating a Taurus object by composing a `QObject` with a `TaurusBaseComponent`
would be replaced by decorating the `QObject` with a class decorator (
called e.g. `@taurusmodel`) which would monkey-patch the decorated class to
insert the model API. In this way, if the `@taurusmodel` decorator accepts an
optional `key` argument, the names of the inserted methods could include the key
in their name. For example, a multi-model `TaurusLabel` could be implemented as:

```python
@taurusmodel()
@taurusmodel(key="Background")
class TaurusLabel(Qt.QLabel):
    ...
```

and this would result in a the `TaurusLabel` class exposing the "
standard" `setModel()`, `getModelObj()`, etc. **plus** `setBackgroundModel()`
, `getBackgroundModelObj()`, etc.

This implementation is very appealing but it has been discarded (for now) in
favour of the proposed one because of:

1. its implementation being considerably more complex
2. maintaining backwards compatibility being more difficult
3. monkey-patched classes being more difficult to debug
4. IDE auto-completion and linting issues with monkey-patched methods

## License

Copyright (c) 2021 Carlos Pascual-Izarra

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom
the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Changes

- 2021-09-06 [Carlos Pascual][]. Initial version
- 2021-09-09 [Carlos Pascual][]. Completed draft 
- 2021-12-17 [Carlos Pascual][]. Added more details on implementation
- 2021-12-17 [Carlos Pascual][]. Promoted to CANDIDATE 
- 2021-12-23 [Carlos Pascual][]. Changed implementation details of the model-
  container use case support
- 2022-02-09 [Carlos Pascual][]. Promoted to ACCEPTED

[Carlos Pascual]: https://gitlab.com/c-p
