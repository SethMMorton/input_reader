#ifndef INPUT_READER_H
#define INPUT_READER_H

/***********************************************************************
 * Convenience functions for dealing with python's C API, specifically *
 * for using the input_reader module from C.                           *
 * This is a header-only "library".                                    *
 ***********************************************************************/

#include <Python.h>

/* Define "bool" if not C++ */
#ifndef __cplusplus
/* Use stdbool.h if available */
#if __STDC_VERSION__ >= 199901L
#include <stdbool.h>
#else
typedef int bool;
const bool false = 0;
const bool true  = 1;
#endif
#endif

/*! \brief Add a custom search path to sys.path.
 *
 * \param path    The path to add to sys.path.
 * \param prepend Indicates you want to put the path at the front of sys.path
 *                instead of the end of sys.path.
 * \return        1 if unsuccessful, 0 otherwise.
 */
inline int AddCustomPythonSearchPath(const char* path, bool prepend)
{
    PyObject *sys_path = PySys_GetObject(const_cast<char*>("path"));
    if (not PyList_Check(sys_path))
        return 1;
    PyObject *newpath = PyString_FromString(path);
    if (prepend)
        PyList_Insert(sys_path, (Py_ssize_t) 0, newpath);
    else
        PyList_Append(sys_path, newpath);
    if (PyErr_Occurred())
        return 1;
    Py_XDECREF(newpath);
    return 0;
}

/*! \brief Returns the python traceback from an error.
 *
 * The function checks if there is an error on the stack, and if so
 * returns a minimal traceback message.
 *
 * \return The error message, or NULL if there was no error.
 */
inline const char* GetLastErrorMessage()
{
    /* Short circuit if no error */
    if (not PyErr_Occurred()) return NULL;

    /* Grab the exception data */
    PyObject *exc_type, *exc_value, *exc_traceback;
    PyErr_Fetch(&exc_type, &exc_value, &exc_traceback);
    PyErr_NormalizeException(&exc_type, &exc_value, &exc_traceback);

    /* From the exception data, get the line number of the exception
     * and the file it occured in.
     */
    PyObject *tb_frame  = PyObject_GetAttrString(exc_traceback, "tb_frame");
    PyObject *f_code    = PyObject_GetAttrString(tb_frame, "f_code");
    PyObject *f_globals = PyObject_GetAttrString(tb_frame, "f_globals");
    PyObject *filename  = PyObject_GetAttrString(f_code, "co_filename");
    PyObject *linenum   = PyObject_GetAttrString(exc_traceback, "tb_lineno");

    /* Use linecache to get the line of code that failed */
    PyObject *linecache = PyImport_ImportModule("linecache");
    PyObject_CallMethod(linecache, (char*) "checkcache", (char*) "O", filename);
    PyObject *offending_line = PyObject_CallMethod(linecache, (char*) "getline", (char*) "OOO",
                                                   filename, linenum, f_globals);

    /* From the exception type get the exception name */
    PyObject *exc_name = PyObject_GetAttrString(exc_type, "__name__");

    /* Make a string showing the line number and file */
    PyObject *fmt1 = PyString_FromString("On line {0} of file {1}:");
    PyObject *location = PyObject_CallMethod(fmt1, (char*) "format",
                                             (char*) "OO", linenum, filename);

    /* Make a string of the exception name and message */
    PyObject *fmt2 = PyString_FromString("{0}: {1}");
    PyObject *err_msg = PyObject_CallMethod(fmt2, (char*) "format",
                                            (char*) "OO", exc_name, exc_value);

    /* Now, create a list containing the three lines of the error to show.
     * First, state the line number and file of the error.
     * Then the actual offending line.
     * Last, show the exception and message.
     */
    PyObject *list = PyList_New(0);
    PyList_Append(list, location);
    PyList_Append(list, offending_line);
    PyList_Append(list, err_msg);

    // Extract the full message from the list.
    PyObject *newline = PyString_FromString("\n");
    PyObject *fullmsg = PyObject_CallMethod(newline, (char*) "join", (char*) "O", list);
    const char* msg = PyString_AsString(fullmsg);

    Py_XDECREF(linecache);
    Py_XDECREF(tb_frame);
    Py_XDECREF(f_code);
    Py_XDECREF(f_globals);
    Py_XDECREF(filename);
    Py_XDECREF(linenum);
    Py_XDECREF(offending_line);
    Py_XDECREF(exc_name);
    Py_XDECREF(fmt1);
    Py_XDECREF(fmt2);
    Py_XDECREF(location);
    Py_XDECREF(err_msg);
    Py_XDECREF(list);
    Py_XDECREF(newline);
    Py_XDECREF(fullmsg);
    return msg;
}

/*! \brief Calls a function that reads the input and returns the Namespace object.
 *
 * It is assumed that
 * the given function is a wrapper around the input reader definition
 * then returns the output of the read_input method.
 *
 * Check PyErr_Occured() or GetLastErrorMessage() after calling for errors.
 *
 * \param module   The name of the python module containing the function to call.
 * \param function The name of the function to call.
 * \param input    The name of the file to read.
 * \return         The Namespace object, or NULL if an error occurred.
 */
inline PyObject* CallInputReaderWrapperFunction(const char* module, const char* function, const char* input)
{
    PyObject *mod = PyImport_ImportModule(module);
    if (mod == NULL)
        return NULL;
    PyObject *mod_dict = PyModule_GetDict(mod);
    PyObject *func = PyDict_GetItemString(mod_dict, function);
    if (func == NULL)
        return NULL;
    return PyObject_CallFunction(func, (char*) "s", input);
}

/*! \brief Calls the InputReader object's read_input to return the Namespace.
 * 
 * Extracts appropriate InputReader instance from the given module, and then
 * calls its read_input method. 
 * 
 * Check PyErr_Occured() or GetLastErrorMessage() after calling for errors.
 *
 * \param module   The name of the python module containing the function to call.
 * \param instance The name of the InputReader instance object we will use to
 *                 read the input file.
 * \param input    The name of the file to read.
 * \return         The Namespace object, or NULL if an error occurred.
 */
inline PyObject* CallInputReaderReadInput(const char* module, const char* instance, const char* input)
{
    PyObject *mod = PyImport_ImportModule(module);
    if (mod == NULL)
        return NULL;
    PyObject *mod_dict = PyModule_GetDict(mod);
    PyObject *inst = PyDict_GetItemString(mod_dict, instance);
    if (inst == NULL)
        return NULL;
    return PyObject_CallMethod(inst, (char*) "read_input", (char*) "s", input);
}

/*! \brief Determine if the given attribute is in the Namespace. 
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if it exists, false, if not.
 */
inline bool ExistsInNamespace(PyObject *name_space, const char *attr)
{
    return (bool) PyObject_HasAttrString(name_space, attr);
}

/*! \brief Determine if the given attribute is in the Namespace and is None.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is None, false, if not.
 */
inline bool ExistsInNamespace_IsNone(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool r = val == Py_None;
    Py_XDECREF(val);
    return r;
}

/*! \brief Determine if the given attribute is in the Namespace and is an int.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is an int, false, if not.
 */
inline bool ExistsInNamespace_IsInt(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool r = PyInt_Check(val);
    Py_XDECREF(val);
    return r;
}

/*! \brief Determine if the given attribute is in the Namespace and is a float.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is a float, false, if not.
 */
inline bool ExistsInNamespace_IsFloat(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool r = PyFloat_Check(val);
    Py_XDECREF(val);
    return r;
}

/*! \brief Determine if the given attribute is in the Namespace and is a bool.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is a bool, false, if not.
 */
inline bool ExistsInNamespace_IsBool(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool r = PyBool_Check(val);
    Py_XDECREF(val);
    return r;
}

/*! \brief Determine if the given attribute is in the Namespace and is a str.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is a str, false, if not.
 */
inline bool ExistsInNamespace_IsString(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool r = PyString_Check(val);
    Py_XDECREF(val);
    return r;
}

/*! \brief Determine if the given attribute is in the Namespace and is a sequence.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is a sequence, false, if not.
 */
inline bool ExistsInNamespace_IsSequence(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool r = PySequence_Check(val);
    Py_XDECREF(val);
    return r;
}

/*! \brief Determine if the given attribute is in the Namespace and is a dict.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is a dict, false, if not.
 */
inline bool ExistsInNamespace_IsDict(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool r = PyDict_Check(val);
    Py_XDECREF(val);
    return r;
}

/*! \brief Determine if the given attribute is in the Namespace and is a Namespace.
 * \param name_space The Namespace object.
 * \param attr       The attribute to check.
 * \return           True if the attribute is a Namespace, false, if not.
 */
inline bool ExistsInNamespace_IsSubNamespace(PyObject *name_space, const char *attr)
{
    if (not ExistsInNamespace(name_space, attr)) return false;
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    PyObject *inpread = PyImport_ImportModule("input_reader");
    if (inpread == NULL) {
        Py_XDECREF(val);
        return false;
    }
    PyObject *inpread_dict = PyModule_GetDict(inpread);
    PyObject *Namespace = PyDict_GetItemString(inpread_dict, "Namespace");
    if (Namespace == NULL) {
        Py_XDECREF(val);
        return false;
    }
    bool r = PyObject_IsInstance(val, Namespace);
    Py_XDECREF(val);
    return r;
}

/*! \brief Extract the given attribute from the Namespace as an int.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \return           The value in the attribute as an int.
 */
inline int FromNamespace_AsInt(PyObject *name_space, const char *attr)
{
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    int x = (int) PyInt_AsLong(val);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a double.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \return           The value in the attribute as a double.
 */
inline double FromNamespace_AsDouble(PyObject *name_space, const char *attr)
{
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    double x = PyFloat_AsDouble(val);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a bool.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \return           The value in the attribute as a bool.
 */
inline bool FromNamespace_AsBool(PyObject *name_space, const char *attr)
{
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    bool x = (bool) PyInt_AsLong(val);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a Py_complex.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \return           The value in the attribute as a Py_complex.
 */
inline Py_complex FromNamespace_AsPyComplex(PyObject *name_space, const char *attr)
{
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    Py_complex x = PyComplex_AsCComplex(val);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a const char*.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \return           The value in the attribute as a const char*.
 */
inline const char* FromNamespace_AsString(PyObject *name_space, const char *attr)
{
    PyObject *val = PyObject_GetAttrString(name_space, attr);
    const char* x = PyString_AsString(val);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a PyObject.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * The user will be responsible for decreasing the reference count of the
 * returned object when they are done with it.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \return           The value in the attribute as a PyObject.
 */
inline PyObject* FromNamespace_AsPyObject(PyObject *name_space, const char *attr)
{
    return PyObject_GetAttrString(name_space, attr);
}

/*! \brief Extract a sub-Namespace from the Namespace (i.e. from a block).
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * The user will be responsible for decreasing the reference count of the
 * returned object when they are done with it.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \return           The value in the attribute as a PyObject.
 */
inline PyObject* FromNamespace_SubNamespace(PyObject *name_space, const char *attr)
{
    return PyObject_GetAttrString(name_space, attr);
}

/*! \brief Extract the given attribute from the Namespace as an int at some index in a sequence.
 * It is assumed that the object in the given attribute is some sequence that can
 * be indexed. Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param index      The index in the sequence.
 * \return           The value at the index in the attribute as an int.
 */
inline int FromNamespace_AsInt_AtIndex(PyObject *name_space, const char *attr, int index)
{
    PyObject *seq = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PySequence_GetItem(seq, (Py_ssize_t) index);
    int x = (int) PyInt_AsLong(val);
    Py_XDECREF(seq);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a double at some index in a sequence.
 * It is assumed that the object in the given attribute is some sequence that can
 * be indexed. Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param index      The index in the sequence.
 * \return           The value at the index in the attribute as a double.
 */
inline double FromNamespace_AsDouble_AtIndex(PyObject *name_space, const char *attr, int index)
{
    PyObject *seq = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PySequence_GetItem(seq, (Py_ssize_t) index);
    double x = PyFloat_AsDouble(val);
    Py_XDECREF(seq);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a bool at some index in a sequence.
 * It is assumed that the object in the given attribute is some sequence that can
 * be indexed. Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param index      The index in the sequence.
 * \return           The value at the index in the attribute as a bool.
 */
inline bool FromNamespace_AsBool_AtIndex(PyObject *name_space, const char *attr, int index)
{
    PyObject *seq = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PySequence_GetItem(seq, (Py_ssize_t) index);
    bool x = (bool) PyInt_AsLong(val);
    Py_XDECREF(seq);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a Py_complex at some index in a sequence.
 * It is assumed that the object in the given attribute is some sequence that can
 * be indexed. Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param index      The index in the sequence.
 * \return           The value at the index in the attribute as a Py_complex.
 */
inline Py_complex FromNamespace_AsPyComplex_AtIndex(PyObject *name_space, const char *attr, int index)
{
    PyObject *seq = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PySequence_GetItem(seq, (Py_ssize_t) index);
    Py_complex x = PyComplex_AsCComplex(val);
    Py_XDECREF(seq);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a const char* at some index in a sequence.
 * It is assumed that the object in the given attribute is some sequence that can
 * be indexed. Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param index      The index in the sequence.
 * \return           The value at the index in the attribute as a const char*.
 */
inline const char* FromNamespace_AsString_AtIndex(PyObject *name_space, const char *attr, int index)
{
    PyObject *seq = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PySequence_GetItem(seq, (Py_ssize_t) index);
    const char* x = PyString_AsString(val);
    Py_XDECREF(seq);
    Py_XDECREF(val);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a PyObject at some index in a sequence.
 * It is assumed that the object in the given attribute is some sequence that can
 * be indexed. Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * The user will be responsible for decreasing the reference count of the
 * returned object when they are done with it.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param index      The index in the sequence.
 * \return           The value at the index in the attribute as a PyObject.
 */
inline PyObject* FromNamespace_AsPyObject_AtIndex(PyObject *name_space, const char *attr, int index)
{
    PyObject *seq = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PySequence_GetItem(seq, (Py_ssize_t) index);
    Py_XDECREF(seq);
    return val;
}

/*! \brief Extract the given attribute from the Namespace as an int at some key in a dict.
 * It is assumed that the object in the given attribute is some dict.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param key        The key in the dict.
 * \return           The value at the index in the attribute as an int.
 */
inline int FromNamespace_AsInt_AtKey(PyObject *name_space, const char *attr, const char *key)
{
    PyObject *dict = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PyDict_GetItemString(dict, key);
    int x = (int) PyInt_AsLong(val);
    Py_XDECREF(dict);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a double at some key in a dict.
 * It is assumed that the object in the given attribute is some dict.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param key        The key in the dict.
 * \return           The value at the index in the attribute as a double.
 */
inline double FromNamespace_AsDouble_AtKey(PyObject *name_space, const char *attr, const char *key)
{
    PyObject *dict = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PyDict_GetItemString(dict, key);
    double x = PyFloat_AsDouble(val);
    Py_XDECREF(dict);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a bool at some key in a dict.
 * It is assumed that the object in the given attribute is some dict.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param key        The key in the dict.
 * \return           The value at the index in the attribute as a bool.
 */
inline bool FromNamespace_AsBool_AtKey(PyObject *name_space, const char *attr, const char *key)
{
    PyObject *dict = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PyDict_GetItemString(dict, key);
    bool x = (bool) PyInt_AsLong(val);
    Py_XDECREF(dict);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a Py_complex at some key in a dict.
 * It is assumed that the object in the given attribute is some dict.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param key        The key in the dict.
 * \return           The value at the index in the attribute as a Py_complex.
 */
inline Py_complex FromNamespace_AsPyComplex_AtKey(PyObject *name_space, const char *attr, const char *key)
{
    PyObject *dict = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PyDict_GetItemString(dict, key);
    Py_complex x = PyComplex_AsCComplex(val);
    Py_XDECREF(dict);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a const char* at some key in a dict.
 * It is assumed that the object in the given attribute is some dict.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param key        The key in the dict.
 * \return           The value at the index in the attribute as a const char*.
 */
inline const char* FromNamespace_AsString_AtKey(PyObject *name_space, const char *attr, const char *key)
{
    PyObject *dict = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PyDict_GetItemString(dict, key);
    const char* x = PyString_AsString(val);
    Py_XDECREF(dict);
    return x;
}

/*! \brief Extract the given attribute from the Namespace as a PyObject at some key in a dict.
 * It is assumed that the object in the given attribute is some dict.
 * Check PyErr_Occured() or GetLastErrorMessage() for errors.
 * The user will be responsible for decreasing the reference count of the
 * returned object when they are done with it.
 * \param name_space The Namespace object.
 * \param attr       The attribute to get from the Namespace.
 * \param key        The key in the dict.
 * \return           The value at the index in the attribute as a PyObject.
 */
inline PyObject* FromNamespace_AsPyObject_AtKey(PyObject *name_space, const char *attr, const char *key)
{
    PyObject *dict = PyObject_GetAttrString(name_space, attr);
    PyObject *val = PyDict_GetItemString(dict, key);
    Py_XDECREF(dict);
    return val;
}

#endif /* INPUT_READER_H */
