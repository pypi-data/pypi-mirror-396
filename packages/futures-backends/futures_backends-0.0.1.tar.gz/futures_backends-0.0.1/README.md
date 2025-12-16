
# Futures backends

Selects a concurrent.futures backend at runtime. 

Import this module and you can write your code like this:
```
with futures_backends.select_backend( ) as executor:
    futures = [executor.submit(func, arg) for arg in args]
    for future in as_completed(futures):
        _ = future.result()
```

The backend can then be selected in a different place to the computational code. 

So far, we have:

 - 'loky' : https://github.com/joblib/loky
 - 'thread' : concurrent.futures.ThreadPoolExecutor
 - 'fork' : concurrent.futures.ProcessPoolExecutor with mp_context = 'fork'
 - 'forkserver' : concurrent.futures.ProcessPoolExecutor with mp_context = 'forkserver'
 - 'spawn' : concurrent.futures.ProcessPoolExecutor with mp_context = 'spawn'

In the future we would like to add others like pyslurmutils and mpi4py, etc.


## Credits

Thanks to Google's Gemini and OpenAI's chatgpt for many useful suggestions 
when writing this code.
