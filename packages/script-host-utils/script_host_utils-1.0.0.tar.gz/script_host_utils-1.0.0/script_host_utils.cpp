#define Py_LIMITED_API 0x030b0000

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <string>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <stdexcept>
#include <vector>

static void append_string_with_replace_special_chars(std::string& res, const std::string& str) {
  for (const auto& ch : str) {
    switch (ch) {
      case '\\':
        res += "\\\\";
        break;
      case '\"':
        res += "\\\"";
        break;
      case '\b':
        res += "\\b";
        break;
      case '\f':
        res += "\\f";
        break;
      case '\n':
        res += "\\n";
        break;
      case '\r':
        res += "\\r";
        break;
      case '\t':
        res += "\\t";
        break;
      default:
        res += ch;
        break;
    }
  }
}

static void filtered_item_json_dumps(
    PyObject* obj,
    std::string& res,
    const std::unordered_map<std::string, std::shared_ptr<std::unordered_set<std::string>>>& filters_by_keys,
    const std::unordered_map<std::string, std::string>& mapping,
    const std::shared_ptr<std::unordered_set<std::string>>& filter_by_keys = nullptr) {
  if (PyUnicode_Check(obj)) {
    res += "\"";
    append_string_with_replace_special_chars(res, PyUnicode_AsUTF8AndSize(obj, nullptr));
    res += "\"";
  } else if (PyByteArray_Check(obj)) {
    res += "\"";
    append_string_with_replace_special_chars(res, PyByteArray_AsString(obj));
    res += "\"";
  } else if (PyDict_Check(obj)) {
    res += "{";

    bool is_first = true;
    auto process_dict_item = [&](PyObject* item, const std::string& key) {
      std::shared_ptr<std::unordered_set<std::string>> child_filter_by_keys;
      auto it = filters_by_keys.find(key);
      if (it != filters_by_keys.end()) {
        child_filter_by_keys = it->second;
      }

      if (is_first) {
        is_first = false;
      } else {
        res += ",";
      }

      auto it_mapping = mapping.find(key);
      if (it_mapping != mapping.end()) {
        res += "\"";
        res += it_mapping->second;
        res += "\":";
      } else {
        res += "\"";
        res += key;
        res += "\":";
      }

      filtered_item_json_dumps(item, res, filters_by_keys, mapping, child_filter_by_keys);
    };

    if (filter_by_keys) {
      for (const std::string& key : *filter_by_keys) {
        PyObject* item = PyDict_GetItemString(obj, key.c_str());
        if (item) {
          process_dict_item(item, key);
        }
      }
    } else {
      Py_ssize_t pos = 0;
      PyObject* key = nullptr;
      PyObject* value = nullptr;
      while (PyDict_Next(obj, &pos, &key, &value)) {
        std::string key_str;
        if (PyUnicode_Check(key)) {
          append_string_with_replace_special_chars(key_str, PyUnicode_AsUTF8AndSize(key, nullptr));
        } else if (PyLong_Check(key)) {
          key_str = std::to_string(PyLong_AsLong(key));
        } else if (PyByteArray_Check(key)) {
          append_string_with_replace_special_chars(key_str, PyByteArray_AsString(key));
        } else {
          throw std::runtime_error("unsupported python object key type in dictionary");
        }
        process_dict_item(value, key_str);
      }
    }

    res += "}";
  } else if (PyList_Check(obj)) {
    res += "[";

    Py_ssize_t size = PyList_Size(obj);
    for (Py_ssize_t i = 0; i < size; i++) {
      PyObject* iter_obj = PyList_GetItem(obj, i);

      if (i != 0) {
        res += ",";
      }

      filtered_item_json_dumps(iter_obj, res, filters_by_keys, mapping, filter_by_keys);
    }

    res += "]";
  } else if (PyBool_Check(obj)) {
    if (PyObject_IsTrue(obj)) {
      res += "true";
    } else {
      res += "false";
    }
  } else if (PyLong_Check(obj)) {
    res += std::to_string(PyLong_AsLong(obj));
  } else if (PyFloat_Check(obj)) {
    res += std::to_string(PyFloat_AsDouble(obj));
  } else if (obj == Py_None) {
    res += "null";
  } else {
    throw std::runtime_error("unsupported python object type");
  }
}

struct PythonGilState {
  PyGILState_STATE state;
  PythonGilState(): state(PyGILState_Ensure()) {}
  ~PythonGilState() {PyGILState_Release(state);}
};

static PyObject* filtered_json_dumps(PyObject* self, PyObject* args) {
  PyObject* obj = Py_None;
  PyObject* filter_obj = Py_None;
  PyObject* mapping_obj = Py_None;
  if (!PyArg_ParseTuple(args, "OOO", &obj, &filter_obj, &mapping_obj)) {
    PyErr_SetString(PyExc_RuntimeError, "bad args");
    return 0;
  }

  std::unordered_map<std::string, std::shared_ptr<std::unordered_set<std::string>>> filters_by_keys;
  std::unordered_map<std::string, std::string> mapping;
  std::string res;

  PythonGilState lock;
  if (PyDict_Check(filter_obj)) {
    Py_ssize_t pos = 0;
    PyObject* key = nullptr;
    PyObject* value = nullptr;
    while (PyDict_Next(filter_obj, &pos, &key, &value)) {
      if (!PyUnicode_Check(key)) {
        throw std::runtime_error("the filter object keys are not strings");
      }

      std::string key_str;
      append_string_with_replace_special_chars(key_str, PyUnicode_AsUTF8AndSize(key, nullptr));
      if (PyList_Check(value)) {
        Py_ssize_t size = PyList_Size(value);
        auto exract_keys = std::make_shared<std::unordered_set<std::string>>();
        for (Py_ssize_t i = 0; i < size; i++) {
          PyObject* extract_key_obj = PyList_GetItem(value, i);
          if (PyUnicode_Check(extract_key_obj)) {
            std::string item_str;
            append_string_with_replace_special_chars(item_str, PyUnicode_AsUTF8AndSize(extract_key_obj, nullptr));
            exract_keys->insert(item_str);
          } else {
            throw std::runtime_error("the filter object values is not a string list");
          }
        }
        filters_by_keys[key_str] = exract_keys;
      } else {
        throw std::runtime_error("the filter object values is not a string list");
      }
    }
  } else {
    throw std::runtime_error("the filter object is not a dictionary");
  }

  if (PyDict_Check(mapping_obj)) {
    Py_ssize_t pos = 0;
    PyObject* key = nullptr;
    PyObject* value = nullptr;
    while (PyDict_Next(mapping_obj, &pos, &key, &value)) {
      if (!PyUnicode_Check(key)) {
        throw std::runtime_error("the mapping object keys are not strings");
      }

      std::string key_str;
      append_string_with_replace_special_chars(key_str, PyUnicode_AsUTF8AndSize(key, nullptr));
      if (PyUnicode_Check(value)) {
        std::string value_str;
        append_string_with_replace_special_chars(value_str, PyUnicode_AsUTF8AndSize(value, nullptr));
        mapping[key_str] = value_str;
      } else {
        throw std::runtime_error("the mapping object values are not strings");
      }
    }
  } else {
    throw std::runtime_error("the mapping object is not a dictionary");
  }

  filtered_item_json_dumps(obj, res, filters_by_keys, mapping);
  return PyUnicode_FromString(res.c_str());
}

static size_t levenshtein_distance(const std::string& s1, const std::string& s2) {
  const size_t m = s1.size();
  const size_t n = s2.size();

  if (!m) return n;
  if (!n) return m;

  std::vector<size_t> costs(n+1);
  for (size_t k = 0; k <= n; k++)
    costs[k] = k;

  size_t i = 0;
  for (std::string::const_iterator it1 = s1.begin(); it1 != s1.end(); ++it1, ++i) {
    costs[0] = i+1;
    size_t corner = i;
    size_t j = 0;
    for (std::string::const_iterator it2 = s2.begin(); it2 != s2.end(); ++it2, ++j) {
      size_t upper = costs[j+1];
      if (*it1 == *it2) {
        costs[j+1] = corner;
      } else {
        size_t t = upper < corner ? upper : corner;
        costs[j+1] = (costs[j] < t ? costs[j] : t) + 1;
      }
      corner = upper;
    }
  }
  return costs[n];
}

static PyObject* levenshtein_distance(PyObject* self, PyObject* args) {
  char* s1 = nullptr;
  char* s2 = nullptr;
  if (!PyArg_ParseTuple(args, "ss", &s1, &s2) || !s1 || !s2) {
    PyErr_SetString(PyExc_RuntimeError, "bad args");
    return 0;
  }
  return Py_BuildValue("i", levenshtein_distance(s1, s2));
}

static PyMethodDef methods[] =
{
    {"filtered_json_dumps", filtered_json_dumps, METH_VARARGS, "filtered_json_dumps"},
    {"levenshtein_distance", levenshtein_distance, METH_VARARGS, "levenshtein_distance"},
    {0, 0, 0, 0}
};

static PyModuleDef module =
{
    PyModuleDef_HEAD_INIT,
    "script_host_utils", "script_host_utils", -1, methods
};

PyMODINIT_FUNC PyInit_script_host_utils(void)
{
    return PyModule_Create(&module);
}
