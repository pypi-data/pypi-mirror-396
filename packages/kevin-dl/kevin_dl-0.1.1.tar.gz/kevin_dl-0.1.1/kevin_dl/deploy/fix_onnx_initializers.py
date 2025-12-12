import onnx
from onnx import helper, checker


def fix_onnx_initializers(input_model_path: str, output_model_path: str):
    # 1. 加载原始模型
    model = onnx.load(input_model_path)

    # 2. 提取并保留 opset_imports
    opset_imports = list(model.opset_import)

    # 3. 构建新的输入列表，剔除与 initializer 同名的输入
    initializer_names = {init.name for init in model.graph.initializer}
    new_inputs = [inp for inp in model.graph.input if inp.name not in initializer_names]

    # 4. 构造新的 GraphProto，保留 initializer 与 value_info
    new_graph = helper.make_graph(
        nodes=list(model.graph.node),
        name=model.graph.name,
        inputs=new_inputs,
        outputs=list(model.graph.output),
        initializer=list(model.graph.initializer),
        value_info=list(model.graph.value_info),
        doc_string=model.graph.doc_string,
    )

    # 5. 构造新的 ModelProto，传入 opset_imports 与 producer_name
    new_model = helper.make_model(
        new_graph,
        producer_name=model.producer_name,
        opset_imports=opset_imports
    )

    # 6. 保留其他元数据
    new_model.ir_version = model.ir_version
    new_model.metadata_props.extend(model.metadata_props)

    # 7. 校验并保存
    checker.check_model(new_model)
    onnx.save(new_model, output_model_path)
    print(f"模型已修复并保存到: {output_model_path}")
