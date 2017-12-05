# How to Import from another .params file
**Description**: This tutorial will show you how to import a .params file from another ROS package instead of copy-pasting it all over.
**Tutorial Level**: ADVANCED

## Setup

Note that your package will still need to depend on rosparam_handler and dynamic_reconfigure.

You can find an example of a minimal package called [imported_rosparam_handler_test](https://github.com/awesomebytes/imported_rosparam_handler_test) which imports from [rosparam_handler_tutorial](https://github.com/cbandera/rosparam_handler_tutorial).


## The params File

```python
#!/usr/bin/env python
from rosparam_handler.parameter_generator_catkin import *
gen = ParameterGenerator()
# Do it at the start, as it overwrites all current params
gen.initialize_from_file('rosparam_handler_tutorial', 'Demo.params', relative_path='/cfg/')

# Do your usual business
gen.add("some_other_param", paramtype="int",description="Awesome int", default=2, min=1, max=10, configurable=True)
gen.add("non_configurable_thing", paramtype="int",description="Im not configurable", default=2, min=1, max=10, configurable=False)

# Syntax : Package, Node, Config Name(The final name will be MyDummyConfig)
exit(gen.generate("imported_rosparam_handler_test", "example_node", "Example"))
```

You just need to call `initialize_from_file(ros_package_name, File.params)`. Note that it will overwrite all params. Should be called at the start (that's why it's called initialize).

You have the optional parameter `relative_path` in case you store your .params file somewhere else than in the `/cfg/` folder.