CC1 CLM tests
=============

Scripts in cc1/tests/clm allow to perform tests directly on CLM.
    - mktest-gui.py - run gui version. Allows to manually select test, run it and
      view results.
    - mktest.py [test name|test_number] - start selected test. Console version.
      Results are stored in log.txt and log.html file.

Scenarios are stored in scripts directory.


Before running tests
====================

First, you should configure PYTHONPATH variable. Set it to path, where cm and
clm is installed. Usually it is /opt/cc1 or src directory in clone of git
repository.

Second thing is to edit settings.py file and define what is address of CLM.

Third - rename predefined/users-dev.py to predefined/users.py or put as users.py
your file with predefined accounts (for production cloud access)

Requirements
------------

Install packages:
	- qemu (command qemu-img)
	- libvirt-bin
	- qemu-kvm
	- kvm
	- kvm-pxe
	- qemu-kvm-extras
	- qemu-common
	- python-qt (in case of use graphical interface)
	- python-django (in case of use html results)

Add test user with group membership:
	- kvm
	- libvirtd

Running tests
=============
In graphical tool you can see result of each test, including:
    - function name
    - passed arguments (it is possible to unwrap lists and dictionaries)
    - returned status
    - returned data

Test steps, which have gone wrong are highlighted to red. It is caused by e.g.
CMException, CLMException or wrong response status (different than expected,
what could be defined).

In batch version (mktest.py) you can see whole run in log.txt file (or other,
selected in settings). Log  file has python format. In first two lines are stored
variables, with test run information. Each next line (appending to action list)
contains each step of test.

The last part of log file is the stored_results dictionary. This structure
allows to use function's responses in next steps (e.g. list VMs and destroy
first in next step). You find strict description of stored_objects in next
chapter.


Creating own tests
==================

Each test should contain at least:
- empty actions list - variable actions
- user information - dictionary with fields:
    - l - login
    - p - password
    - cm - default cm id. You could also get default cm id from settings,
      importing it.
    - cm_p - optional, CM admin password

It is possible to use standard python modules in scenario script and python
syntax. The only one requirement is to fill actions list. Each item of this list
is single dictionary, which descripts action

Calling functions
-----------------

Add to actions list dictionary with fields:
- type - (optional) defines, what kind of test is descripted. Allowed values:
    - 'function' - this action describes how to call function. If 'type' is not
      given, this is default behavior
    - 'exec' - execute a command
    - 'sleep' - wait several seonds



Action syntax for functions ('type' == 'function' or without 'type' field):
- u or user - (optional) dictionary with user, who should call function:
    - l - login
    - p - password
    - cm - cm id

  if given, the first three parameters are with user information. After it,
  proper parameters are passed to CLM
- fname - (required) function name, which is registered in clm
- args - (required) function arguments list. If function has no args, then pass
  empty list
- estatus - (optional) excepted function return status (cannot be exception). If
  not given, excepted status is 'ok' (from response)
- store_as - (optional) store result in dictionary under given name to future
  use
- wait_return - (optional) call function, until expression is not true. It could
  be used to wait e.g. vm is in runnung state. The r variable (in expression) is
  data returned by function
- max_wait - (optional) - if wait_return is set, it defines how long test should
  wait
- as_cmadmin - (optional) - if True, command is executed as cm admin. Concenrs
  only admin_cm functions in cm. Flag adds cm_p field from user description as
  third parameter of function. Used with standard (non-cmadmin) functions could
  cause errors!
- predefined_action - (optional) - defines if action is defined in
  predefined/actions.py. Results beautiful light-blue background in test results

Action syntax for sleep ('type' == 'sleep'):
- time - time to sleep (in seconds)

Action syntax for execs ('type' == 'exec'):
- command - (required) command to execute
- args - arguments for command. You can use substitutions like in function
  commands
- stdin - (TODO: optional) - what should be passed to standard input of command
- estatus - (optional) expected return code. Default is 0
- wait_return - (optional) call command, until expression is not true. It could
  be used to wait e.g. ssh on vm is running. Example expression:
  r = 1
  Available variables in expression:
  	- r - return code
  	- stdout - command stanrd output
  	- stderr - command standard error output
- max_wait - (optional) - if wait_return is set, it defines how long test should
  wait to valid response

Action syntax for ping ('type' == 'ping'):
- host - host address to ping
- count - ammount of icmp echo requests


Action syntax for libvirt calls ('type' == 'libvirt'):
- connection - dictionary with fields:
	- driver (e.g. qemu)
	- transport (e.g. ssh)
	- user
	- address
	- suffix (e.g. '/system')
- fname - libvirt's function name to call
- args - argument list
- estatus - (optional) expected return value. Default is True
- wait_return - (optional) call command, until expression is not true. It could
  be used to wait e.g. ssh on vm is running. Example expression:
  r = 1
  Available variables in expression:
  	- r - return code
  	- stdout - command stanrd output
  	- stderr - command standard error output
- max_wait - (optional) - if wait_return is set, it defines how long test should
  wait to valid response


Action syntax for python scripts ('type' == 'pyscript')
- script - string with script to execute
- description
In scripts, there are some predefined variables: r, log, actions
and stored_results. R variable contains result of script execution. By default
it is 'done', but could be changed to 'error' string. Log variable is string with
logs from scripts. It is only way to put any values by this variable.
Actions is actions list from script/scenario and stored_results is list
of previously stored in test function results.

Example:
--------

u_cc1 = {'l': 'cc1', 'p': 'cc1', 'cm': 0}
actions.append({'u': u_cc1, 'fname': 'image.user.list', 'args': [{'access': 0, 'type': 2}], 'store_as': 'user_images', 'estatus': 'ok'})
actions.append({'u': u_cc1, 'fname': 'image.user.list', 'args': [{'access': 0, 'type': 2}], 'wait_return': 'for'})

Preparing parameters with stored_results
----------------------------------------

In some cases you would like to use response from one function as other function
parameter. To do this, put in first function description (action) key store_as.
In above example, this key has value 'user_images'. Response data from
image.user.list will be stored under this name in stored_results dictionary.

To use this value in next action (function call) prepare speciall parameter in
place, where it should be placed. Parameters starting with @ are substituted to
stored_results values. E.g. parameter @['user_images'][1]['id'] will be
substituted to id of second image returned in example (data is stored as
user_images).


Predefined variables, actions and macros
----------------------------------------

In predefined folder you can find some ready-to-use variables:
- actions.py - predefined actions, which are often used, like listing virtual
  machines, listong clusters etc... To use them just append one of this actions
  to your actions list
- macros.py - contains functions, which allows you to easy get values from
  stored_results dictionary. Macros are compatibile with store_as names from
  actions in actions.py file. To use macro (function), just call it in place,
  where you need to insert special value. Functions return strings starting with
  @.
- users.py - standard system users, including default admin (u_admin), cloud
  admin (u_admin_clm), cluster admin (u_admin_cm) and u_new. You could also get
  more accounts, which are stored in test_users list.


Sample BASH aliases to run tests
--------------------------------

export PYTHONPATH=/<repo cc1>/src/:/<repo cc1>/tests/clm/
alias mktest="python /<repo cc1>/tests/clm/mktest.py $1"
alias mktest-gui="python /<repo cc1>/tests/clm/mktest-gui.py"

function mktest-html {
        python /home/tests/cc1/tests/clm/mktest-html.py $1 "/data/tests/results/`date` - $1.html"
}

