# wpy
基于 py3 的一些常用工具

```bash
# 执行测试用例，并校验测试覆盖率，并用 html 格式呈现
> pytest  -v -s --cov --cov-report=html

# 校验某个模块的覆盖率
> pytest  -v -s --cov=wpy.hashs --cov-report=html
```
