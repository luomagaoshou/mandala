Patterns for Incremental Computation & Development
Open In Colab

@op-decorated functions are designed to be composed with one another. This enables the same piece of imperative code to adapt to multiple goals depending on the situation:

saving new @op calls and/or loading previous ones;
cheaply resuming an @op program after a failure;
incrementally adding more logic and computations to the same code without re-doing work.
This section of the documentation does not introduce new methods or classes. Instead, it demonstrates the programming patterns needed to make effective use of mandala's memoization capabilities.

How @op encourages composition
There are several ways in which the @op decorator encourages (and even enforces) composition of @ops:

@ops return special objects, Refs, which prevents accidentally calling a non-@op on the output of an @op
If the inputs to an @op call are already Refs, this speeds up the cache lookups.
If the call can be reused, the input Refs don't even need to be in memory (because the lookup is based only on Ref metadata).
When @ops are composed, computational history propagates through this composition. This is automatically leveraged by ComputationFrames when querying the storage.
Though not documented here, @ops can natively handle Python collections like lists and dicts. This
When @ops are composed in this way, the entire computation becomes "end-to-end memoized".

Toy ML pipeline example
Here's a small example of a machine learning pipeline:


# for Google Colab
try:
    import google.colab
    !pip install git+https://github.com/amakelov/mandala
except:
    pass

from mandala.imports import *
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

@op
def load_data(n_class=2):
    print("Loading data")
    return load_digits(n_class=n_class, return_X_y=True)

@op
def train_model(X, y, n_estimators=5):
    print("Training model")
    return RandomForestClassifier(n_estimators=n_estimators,
                                  max_depth=2).fit(X, y)

@op
def get_acc(model, X, y):
    print("Getting accuracy")
    return round(accuracy_score(y_pred=model.predict(X), y_true=y), 2)

storage = Storage()

with storage:
    X, y = load_data() 
    model = train_model(X, y)
    acc = get_acc(model, X, y)
    print(acc)

Loading data
Training model
Getting accuracy
AtomRef(1.0, hid=d16...)
Retracing your steps with memoization
Running the computation again will not execute any calls, because it will exactly retrace calls that happened in the past. Moreover, the retracing is lazy: none of the values along the way are actually loaded from storage:


with storage:
    X, y = load_data() 
    print(X, y)
    model = train_model(X, y)
    print(model)
    acc = get_acc(model, X, y)
    print(acc)

AtomRef(hid=d0f..., in_memory=False) AtomRef(hid=f1a..., in_memory=False)
AtomRef(hid=caf..., in_memory=False)
AtomRef(hid=d16..., in_memory=False)
This puts all the Refs along the way in your local variables (as if you've just ran the computation), which lets you easily inspect any intermediate variables in this @op composition:


storage.unwrap(acc)

1.0
Adding new calls "in-place" in @op-based programs
With mandala, you don't need to think about what's already been computed and split up code based on that. All past results are automatically reused, so you can directly build upon the existing composition of @ops when you want to add new functions and/or run old ones with different parameters:


# reuse the previous code to loop over more values of n_class and n_estimators 
with storage:
    for n_class in (2, 5,):
        X, y = load_data(n_class) 
        for n_estimators in (5, 10):
            model = train_model(X, y, n_estimators=n_estimators)
            acc = get_acc(model, X, y)
            print(acc)

AtomRef(hid=d16..., in_memory=False)
Training model
Getting accuracy
AtomRef(1.0, hid=6fd...)
Loading data
Training model
Getting accuracy
AtomRef(0.88, hid=158...)
Training model
Getting accuracy
AtomRef(0.88, hid=214...)
Note that the first value of acc from the nested loop is with in_memory=False, because it was reused from the call we did before; the other values are in memory, as they were freshly computed.

This pattern lets you incrementally build towards the final computations you want without worrying about how results will be reused.

Using control flow efficiently with @ops
Because the unit of storage is the function call (as opposed to an entire script or notebook), you can transparently use Pythonic control flow. If the control flow depends on a Ref, you can explicitly load just this Ref in memory using storage.unwrap:


with storage:
    for n_class in (2, 5,):
        X, y = load_data(n_class) 
        for n_estimators in (5, 10):
            model = train_model(X, y, n_estimators=n_estimators)
            acc = get_acc(model, X, y)
            if storage.unwrap(acc) > 0.9: # load only the `Ref`s needed for control flow
                print(n_class, n_estimators, storage.unwrap(acc))

2 5 1.0
2 10 1.0
Memoized code as storage interface
An end-to-end memoized composition of @ops is like an "imperative" storage interface. You can modify the code to only focus on particular results of interest:


with storage:
    for n_class in (5,):
        X, y = load_data(n_class) 
        for n_estimators in (5,):
            model = train_model(X, y, n_estimators=n_estimators)
            acc = get_acc(model, X, y)
            print(storage.unwrap(acc), storage.unwrap(model))

0.88 RandomForestClassifier(max_depth=2, n_estimators=5)
