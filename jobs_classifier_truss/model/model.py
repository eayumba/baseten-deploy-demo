from typing import Any

MODEL_BASENAME = "model"
MODEL_EXTENSIONS = [".joblib", ".pkl", ".pickle"]


class Model:
    def __init__(self, **kwargs) -> None:
        self._data_dir = kwargs["data_dir"]
        config = kwargs["config"]
        model_metadata = config["model_metadata"]
        self._supports_predict_proba = model_metadata["supports_predict_proba"]
        self._model_binary_dir = model_metadata["model_binary_dir"]
        self._model = None

    def load(self):
        import joblib

        model_binary_dir_path = self._data_dir / self._model_binary_dir
        paths = [
            (model_binary_dir_path / MODEL_BASENAME).with_suffix(model_extension)
            for model_extension in MODEL_EXTENSIONS
        ]
        model_file_path = next(path for path in paths if path.exists())
        self._model = joblib.load(model_file_path)

    def preprocess(self, model_input: Any) -> Any:
        """
        Incorporate pre-processing required by the model if desired here.

        These might be feature transformations that are tightly coupled to the model.
        """
        import pickle
        import numpy as np

        with open("data/word_vectorizer.pk", "rb") as f:
            self.preloaded_word_vectorizer = pickle.load(f)
        with open("data/char_vectorizer.pk", "rb") as f:
            self.preloaded_char_vectorizer = pickle.load(f)

        tfidf_word = self.preloaded_word_vectorizer.transform(model_input).toarray()
        tfidf_char = self.preloaded_char_vectorizer.transform(model_input).toarray()
        tfidf_out = np.hstack([tfidf_word, tfidf_char])

        model_input = tfidf_out

        return model_input

    def postprocess(self, model_output: Any) -> Any:
        """
        Incorporate post-processing required by the model if desired here.
        """
        return model_output

    def predict(self, model_input: Any) -> Any:
        model_output = {}
        model_input = model_input['input']
        result = self._model.predict(model_input)
        model_output["predictions"] = result
        if self._supports_predict_proba:
            model_output["probabilities"] = self._model.predict_proba(
                model_input
            ).tolist()
        return model_output
