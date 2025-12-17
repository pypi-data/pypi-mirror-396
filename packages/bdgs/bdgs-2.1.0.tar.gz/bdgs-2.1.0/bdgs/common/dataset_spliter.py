from sklearn.model_selection import train_test_split as sk_split

def split_dataset(X, y, test_size=None, random_state=42, **kwargs):
    if not test_size or test_size <= 0:
        return X, None, y, None

    return sk_split(X, y, test_size=test_size, random_state=random_state, **kwargs)

def choose_fit_kwargs(x_train, y_train, validation_data, batch_size=None, epochs=None, verbose="auto"):
    kwargs = {
        "x": x_train,
        "y": y_train,
        "verbose": verbose,
        "batch_size": batch_size,
        "epochs": epochs
    }

    if (validation_data is not None
        and validation_data[0] is not None
        and validation_data[1] is not None):
        kwargs["validation_data"] = validation_data

    return kwargs
