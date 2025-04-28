Quickstart
Open In Colab

mandala eliminates the developer effort typically required to persist, iterate on, query, version and reproduce results of computational projects, such as machine learning experiments.

It works by automatically capturing inputs, outputs, and code (+dependencies) at calls of @op-decorated functions. A ComputationFrame data structure over this information enables easy queries and high-level operations over program traces.


# for Google Colab
try:
    import google.colab
    !pip install git+https://github.com/amakelov/mandala
except:
    pass# Run this if in a Google Colab notebook
The @op decorator: automatic memoization and code tracking
@op tracks the inputs, outputs, code and dependencies of calls to Python functions. The same call is never executed twice:


from mandala.imports import *
import time

storage = Storage( # stores all `@op` calls
    # where to look for dependencies; use `None` to prevent versioning altogether
    deps_path='__main__' 
    ) 

@op
def inc(x):
    print("Hello from inc!")
    time.sleep(1) # simulate a long operation
    return x + 1

with storage: # all `@op` calls inside this block will be stored in `storage`
    start = time.time()
    a = inc(1)
    b = inc(1) # this will not be executed, but reused
    end = time.time()
    print(f'Took {round(end - start)} seconds')

Hello from inc!
Took 1 seconds
ComputationFrames: generalized dataframes for querying saved computations
@ops are designed to be composed with one another like ordinary Python functions. This automatically keeps track of the relationships between all saved objects.

The ComputationFrame data structure is a natural high-level view of these relationships that can be used to explore storage and extract computation traces in a format useful for analysis. It groups together saved @op calls into computational graphs:


@op # define a new @op to compose with `inc`
def add(x, y):
    print("Hello from add!")
    return x + y

with storage:
    for i in range(5):
        j = inc(i)
        if i % 2 == 0:
            k = add(i, j)

# get & visualize the computation frame for all calls to `inc`
cf = storage.cf(inc) 
print('Computation frame for `inc`:')
cf.draw(verbose=True, orientation='LR') # visualize the computation frame

# expand the computation frame to include all calls connected to the calls of
# `inc` through shared inputs/outputs
cf.expand_all(inplace=True) 
print('Expanded computation frame for `inc`:')
cf.draw(verbose=True, orientation='LR', path='test.jpg') # visualize the computation frame

Hello from inc!
Hello from add!
Hello from inc!
Hello from add!
Hello from inc!
Hello from inc!
Hello from add!
Computation frame for `inc`:
svg


Expanded computation frame for `inc`:
svg

Computation frames generalize dataframes to operate over computation traces
columns are replaced by a computational graph: functions whose input/output edges connect to variables.
rows are replaced by computation traces: variable values and function calls that (possibly partially) follow this graph
A dataframe can be extracted from any computation frame for easier later analysis: - the columns are the nodes in the graph (functions and variables) - each row is a computation trace, possibly padded with NaNs where no value/call is present:


print(cf.df().to_markdown())

|    |   x | inc                   |   var_0 | add                   |   var_1 |
|---:|----:|:----------------------|--------:|:----------------------|--------:|
|  0 |   3 | Call(inc, hid=f62...) |       4 |                       |     nan |
|  1 |   2 | Call(inc, hid=ec7...) |       3 | Call(add, hid=d3f...) |       5 |
|  2 |   4 | Call(inc, hid=f05...) |       5 | Call(add, hid=5f0...) |       9 |
|  3 |   0 | Call(inc, hid=52f...) |       1 | Call(add, hid=38e...) |       1 |
|  4 |   1 | Call(inc, hid=66c...) |       2 |                       |     nan |
Automatic per-call versioning w/ dependency tracking
Changing memoized functions may invalidate their past calls - but not all changes invalidate all calls, and some "non-semantic" changes invalidate no calls at all.

To help with that, mandala can automatically track marked (with @track) dependencies of each call to an @op, and watch for changes in their code:


from unittest.mock import patch
from mandala.utils import mock_input # to simulate user input non-interactively

@op # define a new @op to compose with `inc`
def add(x, y):
    print("Hello from add!")
    return x + square(y)

@track # dependency tracking decorator
def square(num):
    return num**2

# same computations as before, change to `add` will be detected
with patch('builtins.input', mock_input(['y'])):
    with storage:
        for i in range(5):
            j = inc(i)
            if i % 2 == 0:
                k = add(i, j)

CHANGE DETECTED in add from module __main__
Dependent components:
  Version of "add" from module "__main__" (content: 7cd06a0178abc60d137bb47bceafa5f9, semantic: 455b6b8789fb67940e41dbbb135292f7)
╭───────────────────────────────────────────────────── Diff ──────────────────────────────────────────────────────╮
│   1  def add(x, y):                                                                                             │
│   2      print("Hello from add!")                                                                               │
│   3 -    return x + y                                                                                           │
│   4 +    return x + square(y)                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Does this change require recomputation of dependent calls?
WARNING: if the change created new dependencies and you choose 'no', you should add them by hand or risk missing changes in them.
Answer: [y]es/[n]o/[a]bort 
You answered: "y"
Hello from add!
Hello from add!
Hello from add!
Now we've created a new, semantically distinct version of add. The versions and their dependencies can be inspected with the .versions method:


storage.versions(add)
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ### Dependencies for version of function add from module __main__                                               │
│ ### content_version_id=7cd06a0178abc60d137bb47bceafa5f9                                                         │
│ ### semantic_version_id=455b6b8789fb67940e41dbbb135292f7                                                        │
│                                                                                                                 │
│ ################################################################################                                │
│ ### IN MODULE "__main__"                                                                                        │
│ ################################################################################                                │
│                                                                                                                 │
│ @op # define a new @op to compose with `inc`                                                                    │
│ def add(x, y):                                                                                                  │
│     print("Hello from add!")                                                                                    │
│     return x + y                                                                                                │
│                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ ### Dependencies for version of function add from module __main__                                               │
│ ### content_version_id=6001cb6bf4c98e8a1b1a2f9170c7dd14                                                         │
│ ### semantic_version_id=d1bae9c7d7f59e37d04dcb80adc06138                                                        │
│                                                                                                                 │
│ ################################################################################                                │
│ ### IN MODULE "__main__"                                                                                        │
│ ################################################################################                                │
│                                                                                                                 │
│ @op # define a new @op to compose with `inc`                                                                    │
│ def add(x, y):                                                                                                  │
│     print("Hello from add!")                                                                                    │
│     return x + square(y)                                                                                        │
│                                                                                                                 │
│ @track # dependency tracking decorator                                                                          │
│ def square(num):                                                                                                │
│     return num**2                                                                                               │
│                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Conclusion
This was a very brief tour through the three main tools mandala offers: memoization, computation frames, and versioning. Later tutorials will explore these concepts in more complex situations, as well as in more realistic settings such as small machine learning projects.

Made with Material for MkDocs