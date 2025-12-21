`textcomps version 1.2.0.alpha`

## 概论
`textcomps` 是属于`miststar-mccbuilder`的Minecraft BE TextComponent (俗称t显)快速构建库. 它基于 Python 的类型注解特性, 能够为你的需求实现提供便捷灵活的支持.

需要注意的是, textcomps 支持版本在 **Python 3.10** 及以上

### 基础工作流
textcomps 为你提供了一套完整的从**t显的解析/输出**的工具链.

具体来说, 实现了从Dictionary到组件的互转换, 从Dictionary到JSON的互转换, 从JSON到组件的转换.


同时, 当Dictionary或JSON被解析为对象后, textcomps 也提供了一套完整的**构造/解析函数**来进行新对象的构造. 当然也提供了直接构造的支持.

### 完整的类型注解
textcomps 参考 **PEP 484** 实现了类型注解, 通过 `mypy` 检查. 配合编辑器的类型推导功能, 能将绝大多数的 Bug 杜绝在编辑器中 (**编辑器支持**).

### 模板构建
textcomps 1.2.0 中提供了一套类似于 **Python f-string** 的快速构建t显的方式, 我们将其称为**模板构建(template)**. 模板的形式也类似于 f-string, 同时容错率更高. 
在此基础上也提高了构建t显函数的可读性. 使**构建t显的函数**从原来的脚本变成了一个**结构化, 可视化的文档**.

### 你应该从哪里开始?
textcomps 中一个构建t显包含了很多种构建方式, 例如: 模板构建, 流式add构造, 流式translate构造, 智能解析函数adx等.

如果你需要快速构建, 同时不想了解太多底层细节那你完全可以使用**模板构建/流式translate构造**.

如果你更需要**精细化的控制, 或者对库进行扩展**. 那么也不妨使用传统的构建方法.

