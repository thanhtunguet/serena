# The Serena JetBrains Plugin

The [JetBrains Plugin](https://plugins.jetbrains.com/plugin/28946-serena/) allows Serena to
leverage the powerful code analysis capabilities of JetBrains IDEs,
which offers several advantages over the default language server approach.

The proceeds from the plugin also allow us to dedicate more resources to further developing and improving Serena.
We recommend the JetBrains plugin as the preferred way of using Serena, regardless of your choice of code editor.

After purchasing and installing the plugin, you need to configure `jetbrains: True` in your `serena_config.yml`.
Then Serena will automatically connect to an open JetBrains IDE instance.

## Advantages of the JetBrains Plugin

There are multiple features that are only available when using the JetBrains plugin:

- External libraries are indexed and can be referenced by Serena.
- No additional runtime resources or downloads are needed for language servers.
- Faster performance of tools.
- First-class support for multiple languages and frameworks in a single project.

We are also working on additional features like a `move_symbol` tool and debugging related capabilities that
will be available exclusively through the JetBrains plugin at first.


## Usage with Other Editors

We realize that not everyone uses a JetBrains IDE as their main code editor.
You can still take advantage of the JetBrains plugin by running a JetBrains IDE instance alongside your
preferred editor. Most JetBrains IDEs have a free community edition that you can use for this purpose.
You just need to make sure that the project you are working on is open and indexed in the JetBrains IDE, 
so that Serena can connect to it.
