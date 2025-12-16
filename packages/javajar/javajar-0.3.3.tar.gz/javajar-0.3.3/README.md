# JavaJar - Python Java Runner with Auto JDK Management

JavaJar 是一个 Python 工具，可以通过 Python 运行 Java JAR 文件，并自动下载和管理 Java 运行环境。它支持本地 JAR 文件执行和
Maven 仓库依赖解析。

## 解决什么问题？

目前大多数本地（local）MCP 服务器基于 Node.js 或 Python 开发，因为它们可以通过 npx 或 uvx 命令快速配置并启动。

而 Java 编写的 MCP 通常以远程（remote）服务器形式运行，通过 SSE 提供服务，几乎没有采用 stdio 方式交互的本地实现，主要原因是
JRE 需要额外安装和手动配置。

本项目通过自动化管理 Java 运行环境，实现了类似 npx、uvx 的便捷体验，使基于 Java 的本地 MCP 服务器也能一键启动。

## 功能特性

- 🚀 **自动 JDK 管理**: 自动检测、下载和安装所需的 Java 版本
- 📦 **Maven 支持**: 直接从 Maven 仓库下载并运行 JAR 文件，基于spring boot的 mcp 可以build为一个jar文件部署到仓库
- 📋 **环境列表**: 查看系统中所有可用的 Java 版本

## 使用案例

配置local mcp server:

- 自动配置JDK： 其中 `javajar`  会检测 本地是否安装 jdk 17，如果没有会自动下载安装。
- 下载jar: 从配置的maven仓库下载 maven 组件。
  ![](docs/images/mcp_config_1.png)

mcp server配置完成效果：
![](docs/images/mcp_config_2.png)

## 安装与使用

使用 uvx javajar 命令运行，javajar 组件提供了 2 个命令。

- `javajar run`: 运行 JAR 文件

- `javajar java-lsit`: 列出系统中所有可用的 Java 版本

`java-list`命令比较简单，列出 javajar 组件能够识别和管理的java版本

```shell
➜  ~ uvx javajar java-list
检查到以下可用的java版本
17.0.14 -> /Users/yanglikun/.jenv/versions/17/bin/java
17.0.14 -> /Users/yanglikun/.jenv/shims/java
17.0.17 -> /Users/yanglikun/.ylk_javajar/jdkinstall/17/bin/java
1.8.0_472 -> /Users/yanglikun/.ylk_javajar/jdkinstall/8/bin/java
21.0.9 -> /Users/yanglikun/.ylk_javajar/jdkinstall/21/bin/java
```

### javajar run 运行jar

运行jar有两种方式，一种是本地的jar，一种是maven仓库的jar。

#### 本地jar

```json
{
  "ylk-java-mcp": {
    // mcp工具名称，随意修改
    "command": "uvx",
    "args": [
      "javajar",
      "run",
      "--jar=/Users/yanglikun/workspace/ai/ylk-stdio-mcp-java/target/ylk-mcp-stdio-java-0.0.1-SNAPSHOT.jar",
      "--jar-args=--amap.key=xxx"
    ],
    "disabled": false,
    "autoApprove": []
  }
}
```

`--jar=xx.jar`:配置jar的绝对地址
`--jar-args`: 配置jar的参数，比如spring @Value("${amap.key}")占位符，都可以在这里指定。

#### maven仓库的jar

```json
{
  "ylk-java-mcp": {
    "command": "uvx",
    "args": [
      "javajar",
      "run",
      "--maven=com.jd.ylk.ai:ylk-mcp-stdio-java:0.0.1-SNAPSHOT",
      "--release-repo=https://artifactory.jd.com/libs-releases",
      "--snapshot-repo=http://artifactory.jd.com/libs-snapshots",
      "--jar-args=--amap.key=xxx"
    ],
    "disabled": false,
    "autoApprove": []
  }
}
```

和本地jar不同的是 需要指定 maven 坐标 和 仓库地址。默认是从 maven的中心仓下载：https://repo1.maven.org/maven2
`--maven=com.jd.ylk.ai:ylk-mcp-stdio-java:0.0.1-SNAPSHOT`: maven坐标
`--release-repo=https://artifactory.jd.com/libs-releases`: 配置maven release仓库地址,默认从maven central仓库下载
`--snapshot-repo=http://artifactory.jd.com/libs-snapshots`: 配置maven snapshots仓库地址,默认从maven central仓库下载

#### 其它参数
`java_version=17`: 指定java版本，默认是17。可以根据需要指定，也可以配置 17+代表至少要 jdk17。



## jdk和jar在那里
自动下载的jdk和从maven仓库下载的jar在本地哪里呢？

- jdk 在 `~/.ylk_javajar/jdkinstall` 目录下
- jar 在 `~/.ylk_javajar/jars` 目录下

## 开发

### 项目结构

```
javajar/
├── src/javajar/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # 命令行接口
│   ├── java_runner.py      # JAR 执行逻辑
│   ├── jdk_manager.py      # JDK 管理
│   ├── java_list.py        # Java 版本列表
│   └── maven_resolver.py   # Maven 依赖解析
├── tests/                  # 测试文件
├── pyproject.toml         # 项目配置
└── README.md
```

### 下载和构建

```bash
git clone <repository-url>
uv sync
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请在 GitHub Issues 中提交。