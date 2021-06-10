# RExam Item Editor

**Maintaining and editing databases of RExam items**

Feature overview

* Validations checks
    *  file and folder naming and required meta-information 
    * required subfolder structure
    * joining bilingual items in the database (Dutch, English)
* Convenience functions for item editing
    * support for generating and naming new items
    * auto-fix function for some violations of the conventions and *R*  
      markdown syntax
    * multiple choice items: correct answers can be indicated with an `#` 
      (instead of `*`). `exsolution` will be set automatically.
* R markdown rendering check (experimental, requires *R*)

*Released under the MIT License*

Oliver Lindemann, Erasmus University Rotterdam, NL

 
## Dependencies

Python 3.5+ and the following libraries:
* PySimpleGUI
* appdirs

Optional requirement:
* rpy2 >=3.4


## Rendering Rmd File (work in progress)

To render Rmd files directly via the *StatsShare-Item-Editor*, you need 
a functioning 
installation of *R* including the *R*-package `exams`. 

If you don't use the Windows executable, install the Python-package `rpy2` (`pip install rpy2`). 

Windows user find two executable files for *StatsShare-Item-Editor*, one with
and one without *R* rendering support. *StatsShare-Item-Editor* with 
rendering does not work on computers  without a *R* installation.