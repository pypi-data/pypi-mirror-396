    Title: Migrate to gitlab.com
    TEP: 19
    State: ACCEPTED
    Date: 2021-03-17
    Drivers: Carlos Pascual-Izarra cpascual@cells.es
    URL: http://www.taurus-scada.org/tep?TEP19.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
     Move the project hosting from github.com to gitlab.com
 
## Introduction & background

Hosting Taurus in [gitlab.com](GL) was already considered when we 
[migrated](TEP16) to [github.com](GH) (GH) from SourceForge. With the 
acquisition of GH by Microsoft, the idea of moving from GH to GL was considered, 
but never acted upon (see https://github.com/taurus-org/taurus/issues/761).

The interest in this proposal was renewed with the announcement that Travis
would discontinue its unlimited CI support for Free Software Projects (see
https://github.com/taurus-org/taurus/issues/1139#issuecomment-723565619 ) and 
the resulting decision by the Tango community to move its projects to GL
( https://github.com/tango-controls/TangoTickets/issues/47 ).

This TEP proposes to take the chance of the forced CI refactoring because of 
discontinued Travis support to do the move to GL. The pros and cons of this 
option versus staying in GH (and refactor the CI to use GH actions) have been 
already discussed (see https://gitlab.com/tango-controls/cppTango/-/issues/812),
but here we just point the main reasons:

- Freedom: GL is based on Free Software while GH is not.
- Avoid vendor lock-in: GL free nature implies that in the worst case we could 
  move to a self-hosted instance without affecting our project configurations.
- Homogenizing enviroments: most institutes in the taurus community already run
  their own GL instances on-premises. Having tango on GL would facilitate 
  transferring projects from local GL instances to community-shared projects. 
  Also, it would facilitate community learning and cooperating since we would 
  be using the same interface and environment both internally and externally.
- Packaging: Gitlab is already used for debian packaging of taurus. Using it for 
  development too helps for integrating the development with the packaging.
- Tango projects are also migrating to GL

## Scope

The following taurus-org hosted projects are to be moved to gitlab 
(in this order):

- https://github.com/taurus-org/taurus
- https://github.com/taurus-org/taurus_pyqtgraph
- https://github.com/taurus-org/taurus_tangoarchiving
- https://github.com/taurus-org/h5file-scheme
- https://github.com/taurus-org/pandas-scheme

## Implementation

The repository migration was executed on **2021-03-17**

Before the migration date, the following tasks were done:

- Notify the taurus mailing lists about the migration 
- Notify all participants (commenters, contributors, etc) and ask them to
  log at least once in GL in order to be able to map their GH and GL accounts
  during the migration. The deadline for the log-ins is 1 day before the 
  migration date of the taurus project.
- Set-up test repositories in GL for preparing the CI migration of taurus and taurus_pyqtgraph

On the migration date, the following tasks were done:

- add a "moved-to-gitlab" branch to the GH repos and set it as the default branch
- set the GH projects in read-only mode (archive them) 
- import them using the ([AdminBot][] account) into https://gitlab.com/taurus-org group 

After the import in GL, the following tasks need to be done:

- Set-up CI in GL
- Implement taurus docs build in GL pages (open a separate MR in GL for that)
- Fix hardcoded links in docs (open a separate MR in GL for that)
- Redirect taurus-scada.org domains to GL pages


## Links to more details and discussions

- Discussions for this TEP are conducted in its associated Pull Request:
https://gitlab.com/taurus-org/taurus/-/merge_requests/1179

- Initial proposal and motivation can be found in this issue: 
https://gitlab.com/taurus-org/taurus/-/issues/761

- Debate in Tango community about migration to gitlab: 
https://gitlab.com/tango-controls/cppTango/-/issues/812

- Sardana discussed this same move but decided to wait for now:
https://github.com/sardana-org/sardana/issues/1433

- Tools for helping with the migration: 
https://github.com/tango-controls/gitlab-migration-tools


## License

Copyright (c) 2021 Carlos Pascual-Izarra

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Changes


- 2021-03-08 [Carlos Pascual][]. Initial version
- 2021-03-17 [Carlos Pascual][]. Migration succeeded
- 2021-03-18 [Carlos Pascual][]. Changing status to ACCEPTED without formal vote (*fait accompli*)


[GH]: https://github.com
[GL]: https://gitlab.com
[TEP16]: http://www.taurus-scada.org/tep?TEP16.md
[AdminBot]: https://gitlab.com/sf-migrator-bot
[Carlos Pascual]: https://gitlab.com/c-p
