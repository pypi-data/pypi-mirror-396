from setuptools import Extension, setup


setup(
    ext_modules=[
        Extension(
            name="script_host_utils",
            py_limited_api=True,
            sources=["script_host_utils.cpp"],
        ),
    ],
)
