# pytest-collect-requirements

A pytest plugin to collect test requirements from tests marked with the `@pytest.mark.requirements(...)` marker. <br>
This plugin allows you to specify requirements for your tests and collect them without executing the tests themselves.

---

## Features
- ✅ addoption `--collect-requirements` to collect requirements without running tests
- ✅ Collect requirements from tests using the `@requirements()` marker
- ✅ Flexible keyword arguments support for any requirement metadata (e.g., cloud instances, regions, resources)
- ✅ Automatic collection and store the requirements in json file
- ✅ Seamless integration with pytest's marker system

---

## Installation
```bash
pip install pytest-collect-requirements
```

---

## Usage Examples

### Basic Usage

Mark your tests with the `@requirements()` marker to specify infrastructure requirements:

```python
import pytest

@pytest.mark.requirements(cloud_instance="c5.large", region="eu-west-1")
def test_my_feature():
    assert 1 == 1
```

### Collecting Requirements

Run pytest with the `--collect-requirements` flag to collect all requirements without executing tests:

```bash
pytest --collect-requirements
```

This will collect all requirements from tests marked with `@requirements()` and store them in the pytest config for later use.

### Multiple Requirements

You can mark multiple tests with different requirements:

```python
import pytest

@pytest.mark.requirements(cloud_instance="c5.large", region="eu-west-1")
def test_requirements():
    assert 1 == 1

@pytest.mark.requirements(cloud_instance="c5.small", region="eu-west-2")
def test_requirements2():
    assert 1 == 1
```

### Custom Requirement Parameters

The `@requirements()` marker accepts any keyword arguments, allowing you to define custom requirement metadata:

```python
import pytest

@pytest.mark.requirements(
    cloud_instance="c5.large",
    region="eu-west-1",
    storage="100GB",
    network="high-speed"
)
def test_with_custom_requirements():
    assert 1 == 1
```

---

## 🤝 Contributing

If you have a helpful tool, pattern, or improvement to suggest:
Fork the repo <br>
Create a new branch <br>
Submit a pull request <br>
I welcome additions that promote clean, productive, and maintainable development. <br>

---

## 🙏 Thanks

Thanks for exploring this repository! <br>
Happy coding! <br>
