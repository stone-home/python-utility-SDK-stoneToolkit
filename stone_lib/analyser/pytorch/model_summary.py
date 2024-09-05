from torchinfo import summary, ModelStatistics
from torchinfo.layer_info import LayerInfo
from collections import defaultdict
from typing import Dict


class ModelSimulator:
    def __init__(self, model: 'torch.nn.Module', input_data: 'torch.Tensor'):
        self._model: 'torch.nn.Module' = model
        self._data: 'torch.Tensor' = input_data
        self._layer_info: Dict[str, LayerInfo] = self._model_summary()

    def _model_summary(self) -> Dict[str, LayerInfo]:
        _model_statis: ModelStatistics = summary(
            model=self._model,
            input_data=self._data,
            device="cpu",
            mode="train",
            depth=10,
        )
        return self._reindex_layers(_model_statis)

    def _reindex_layers(self, model_statistic: ModelStatistics) -> Dict[str, LayerInfo]:
        _index_order: Dict[str, int] = defaultdict(int)
        _leaf_layers: Dict[str, LayerInfo] = {}

        for _layer in model_statistic.summary_list:
            _layer_name: str = _layer.class_name

            _current_index = _index_order[_layer_name]
            _index_order[_layer_name] += 1

            if _layer.is_leaf_layer:
                _layer_trace = [f"{_layer.class_name}_{_current_index}"]

                _parent_layer = _layer.parent_info
                while _parent_layer:
                    _parent_index = _index_order[_parent_layer.class_name] - 1  # 父节点索引已经递增，所以要减1
                    _layer_trace.append(f"{_parent_layer.class_name}_{_parent_index}")
                    _parent_layer = _parent_layer.parent_info

                _layer_trace.reverse()
                _layer_trace_str = "->".join(_layer_trace)

                _leaf_layers[_layer_trace_str] = _layer

        return _leaf_layers

    def get_layer_summary(self):
        _layer_json = []
        for trace, _layer in self._layer_info.items():
            _layer_json.append({
                "layer": trace,
                "input_shape": _layer.input_size,
                "output_shape": _layer.output_size,
                "weight_size": getattr(getattr(_layer.module, "weight", None), "shape", []),
                "bias_size": getattr(getattr(_layer.module, "bias", None), "shape", []),
                "output_bytes": _layer.output_bytes,
                "params_bytes": _layer.param_bytes
            })
        return _layer_json
