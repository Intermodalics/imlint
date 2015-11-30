imlint
=======

Catkin macros which provide standard linter configurations for C++ and Python.

# Usage
Add a test dependency on imlint to your package's package.xml:
```
<test_depend>imlint</test_depend>
```
**Note:** It is recommended to use version 2 of the package manifest format ([REP-140](http://www.ros.org/reps/rep-0140.html)) for correct handling of dependencies specified in the `<test_depend>` element.

In your package's CMakeLists.txt file, include imlint as one of your catkin
component dependencies, ideally you put all imlint related cmake code within a 
```if (CATKIN_ENABLE_TESTING) ... endif()``` block:
```
find_package(imlint REQUIRED)
```
Then, invoke the imlint functions from your CMakeLists.txt, eg:
```
imlint_cpp()
```
If you'd like more control over what gets linted, you can specify the exact
files:
```
imlint_cpp(src/foo.cpp src/bar.cpp src/baz.cpp)
```
To run imlint against your package you must invoke catkin_make with your
package's ```imlint``` target.
For example, for a package named ```my_fancy_package``` you would run:
```
catkin_make imlint_my_fancy_package
```
See the following section for all available functions.

# Reference
Each ```imlint_```* function create a catkin build target called
```imlint_''pkgname''```, which runs all specified lint operations for the
package. Each additionally creates (if it does not yet exist) a master
```imlint``` target, which depends on all other imlint_* targets.

Each function can be called multiple times, if that's more convenient.
  * ```imlint_cpp([files ...])```
  Lint the specified files using a modified cpplint. If none are specified, default to a glob of all cpp and h files contained in the package.
  * ```imlint_python([files ...])```
  Lint the specified files using pep8. If none are specified, default to a glob of all py files contained in the package. This will not catch extensionless executables living in the scripts directory.
  * ```imlint_custom(linter linter_opts file [...])```
  Lint the specified files using a custom lint executable.
  * ```imlint_add_test()```
  Create a dependency between the package's run_tests target and lint target, so that linter fails are able to break the build.
