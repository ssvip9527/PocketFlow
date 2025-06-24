# cookbook/pocketflow-thinking/nodes.py
from pocketflow import Node
import yaml
from utils import call_llm
import textwrap

# 用于打印结构化计划的辅助函数
def format_plan(plan_items, indent_level=0):
    indent = "  " * indent_level
    output = []
    if isinstance(plan_items, list):
        for item in plan_items:
            if isinstance(item, dict):
                status = item.get('status', 'Unknown')
                desc = item.get('description', 'No description')
                result = item.get('result', '')
                mark = item.get('mark', '') # For verification etc.

                # Format the main step line
                line = f"{indent}- [{status}] {desc}"
                if result:
                    line += f": {result}"
                if mark:
                    line += f" ({mark})"
                output.append(line)

                # Recursively format sub-steps if they exist
                sub_steps = item.get('sub_steps')
                if sub_steps:
                    output.append(format_plan(sub_steps, indent_level + 1))
            elif isinstance(item, str): # Basic fallback for string items
                 output.append(f"{indent}- {item}")
            else: # Fallback for unexpected types
                 output.append(f"{indent}- {str(item)}")

    elif isinstance(plan_items, str): # Handle case where plan is just an error string
        output.append(f"{indent}{plan_items}")
    else:
        output.append(f"{indent}# Invalid plan format: {type(plan_items)}")

    return "\n".join(output)

# 用于格式化提示中结构化计划的辅助函数（简化视图）
def format_plan_for_prompt(plan_items, indent_level=0):
    indent = "  " * indent_level
    output = []
    # 简化格式以提高提示清晰度
    if isinstance(plan_items, list):
        for item in plan_items:
            if isinstance(item, dict):
                status = item.get('status', 'Unknown')
                desc = item.get('description', 'No description')
                line = f"{indent}- [{status}] {desc}"
                output.append(line)
                sub_steps = item.get('sub_steps')
                if sub_steps:
                    # 指示嵌套，但不在提示中完全递归显示
                    output.append(format_plan_for_prompt(sub_steps, indent_level + 1))
            else: # Fallback
                 output.append(f"{indent}- {str(item)}")
    else:
        output.append(f"{indent}{str(plan_items)}")
    return "\n".join(output)


class ChainOfThoughtNode(Node):
    def prep(self, shared):
        problem = shared.get("problem", "")
        thoughts = shared.get("thoughts", [])
        current_thought_number = shared.get("current_thought_number", 0)

        shared["current_thought_number"] = current_thought_number + 1

        # 格式化先前的思考并提取最后的计划结构
        thoughts_text = ""
        last_plan_structure = None # 将存储字典列表
        if thoughts:
            thoughts_text_list = []
            for i, t in enumerate(thoughts):
                 thought_block = f"Thought {t.get('thought_number', i+1)}:\n"
                 thinking = textwrap.dedent(t.get('current_thinking', 'N/A')).strip()
                 thought_block += f"  Thinking:\n{textwrap.indent(thinking, '    ')}\n"

                 plan_list = t.get('planning', [])
                 # 使用递归辅助函数进行显示格式化
                 plan_str_formatted = format_plan(plan_list, indent_level=2)
                 thought_block += f"  Plan Status After Thought {t.get('thought_number', i+1)}:\n{plan_str_formatted}"

                 if i == len(thoughts) - 1:
                     last_plan_structure = plan_list # 保留实际结构

                 thoughts_text_list.append(thought_block)

            thoughts_text = "\n--------------------\n".join(thoughts_text_list)
        else:
            thoughts_text = "尚无先前的思考。"
            # 建议使用字典的初始计划结构
            last_plan_structure = [
                {'description': "Understand the problem", 'status': "Pending"},
                {'description': "Develop a high-level plan", 'status': "Pending"},
                {'description': "Conclusion", 'status': "Pending"}
            ]

        # 使用特定辅助函数格式化提示上下文的最后计划结构
        last_plan_text_for_prompt = format_plan_for_prompt(last_plan_structure) if last_plan_structure else "# 没有可用的先前计划。"

        return {
            "problem": problem,
            "thoughts_text": thoughts_text,
            "last_plan_text": last_plan_text_for_prompt,
            "last_plan_structure": last_plan_structure, # Pass the raw structure too if needed for complex updates
            "current_thought_number": current_thought_number + 1,
            "is_first_thought": not thoughts
        }

    def exec(self, prep_res):
        problem = prep_res["problem"]
        thoughts_text = prep_res["thoughts_text"]
        last_plan_text = prep_res["last_plan_text"]
        # last_plan_structure = prep_res["last_plan_structure"] # Can use if needed
        current_thought_number = prep_res["current_thought_number"]
        is_first_thought = prep_res["is_first_thought"]

        # --- 构建提示 ---
        # 已更新为字典结构的指令
        instruction_base = textwrap.dedent(f"""
            你的任务是生成下一个思考（思考 {current_thought_number}）。

            指令：
            1.  **评估先前的思考：** 如果不是第一次思考，通过评估思考 {current_thought_number - 1} 开始 `current_thinking`。说明：“思考 {current_thought_number - 1} 的评估：[正确/小问题/重大错误 - 解释]”。首先处理错误。
            2.  **执行步骤：** 执行计划中 `status: Pending` 的第一个步骤。
            3.  **维护计划（结构）：** 生成一个更新的 `planning` 列表。每个项目都应该是一个字典，包含键：`description`（字符串）、`status`（字符串：“Pending”、“Done”、“Verification Needed”），以及可选的 `result`（字符串，完成时的简洁摘要）或 `mark`（字符串，需要验证的原因）。子步骤由包含这些字典*列表*的 `sub_steps` 键表示。
            4.  **更新当前步骤状态：** 在更新的计划中，将已执行步骤的 `status` 更改为“Done”，并添加一个 `result` 键，其中包含简洁摘要。如果根据评估需要验证，则将状态更改为“Verification Needed”并添加 `mark`。
            5.  **完善计划（子步骤）：** 如果“Pending”步骤很复杂，请在其字典中添加一个 `sub_steps` 键，其中包含一个新步骤字典列表（状态：“Pending”），将其分解。在所有子步骤都“Done”之前，保持父步骤的状态为“Pending”。
            6.  **完善计划（错误）：** 根据评估结果逻辑地修改计划（例如，更改状态，添加更正步骤）。
            7.  **最后一步：** 确保计划朝着最终步骤字典（例如 `{{'description': "Conclusion", 'status': "Pending"}}`）推进。
            8.  **终止：** 仅当执行 `description: "Conclusion"` 的步骤时，才将 `next_thought_needed` 设置为 `false`。
        """)

        # 上下文基本保持不变
        if is_first_thought:
            instruction_context = textwrap.dedent("""
                **这是第一次思考：** 创建一个初始计划作为字典列表（键：description、status）。如果需要，通过 `sub_steps` 键包含子步骤。然后，在 `current_thinking` 中执行第一步，并提供更新的计划（将步骤 1 标记为 `status: Done` 并带有 `result`）。
            """)
        else:
            instruction_context = textwrap.dedent(f"""
                **先前计划（简化视图）：**
                {last_plan_text}

                通过评估思考 {current_thought_number - 1} 开始 `current_thinking`。然后，继续执行 `status: Pending` 的第一步。更新计划结构（字典列表），反映评估、执行和完善。
            """)

        # 已更新为字典结构的输出格式示例
        instruction_format = textwrap.dedent("""
            仅以 ````yaml ... ```` 括起来的 YAML 结构格式化你的响应：
            ```yaml
            current_thinking: |
              # Evaluation of Thought N: [Assessment] ... (if applicable)
              # Thinking for the current step...
            planning:
              # 字典列表（键：description、status、Optional[result、mark、sub_steps]）
              - description: "Step 1"
                status: "Done"
                result: "Concise result summary"
              - description: "步骤 2 复杂任务" # 现在已分解
                status: "Pending" # 父级保持 Pending
                sub_steps:
                  - description: "Sub-task 2a"
                    status: "Pending"
                  - description: "Sub-task 2b"
                    status: "Verification Needed"
                    mark: "思考 X 的结果似乎有误"
              - description: "Step 3"
                status: "Pending"
              - description: "Conclusion"
                status: "Pending"
            next_thought_needed: true # 仅当执行结论步骤时才设置为 false。
            ```
        """)

        # 组合提示部分
        prompt = textwrap.dedent(f"""
            You are a meticulous AI assistant solving a complex problem step-by-step using a structured plan. You critically evaluate previous steps, refine the plan with sub-steps if needed, and handle errors logically. Use the specified YAML dictionary structure for the plan.

            Problem: {problem}

            Previous thoughts:
            {thoughts_text}
            --------------------
            {instruction_base}
            {instruction_context}
            {instruction_format}
        """)
        # --- 结束提示构建 ---

        response = call_llm(prompt)

        # 简单 YAML 提取
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        thought_data = yaml.safe_load(yaml_str) # 可能引发 YAMLError

        # --- 验证（使用 assert） ---
        assert thought_data is not None, "YAML 解析失败，结果为 None"
        assert "current_thinking" in thought_data, "LLM 响应缺少 'current_thinking'"
        assert "next_thought_needed" in thought_data, "LLM 响应缺少 'next_thought_needed'"
        assert "planning" in thought_data, "LLM 响应缺少 'planning'"
        assert isinstance(thought_data.get("planning"), list), "LLM 响应中的 'planning' 不是列表"
        # 可选：如果需要，添加对列表项是否为字典的更深层验证
        # --- 结束验证 ---

        # 添加思考编号
        thought_data["thought_number"] = current_thought_number
        return thought_data


    def post(self, shared, prep_res, exec_res):
        # 将新思考添加到列表
        if "thoughts" not in shared:
            shared["thoughts"] = []
        shared["thoughts"].append(exec_res)

        # 使用更新的递归辅助函数提取计划以进行打印
        plan_list = exec_res.get("planning", ["Error: Planning data missing."])
        plan_str_formatted = format_plan(plan_list, indent_level=1)

        thought_num = exec_res.get('thought_number', 'N/A')
        current_thinking = exec_res.get('current_thinking', 'Error: Missing thinking content.')
        dedented_thinking = textwrap.dedent(current_thinking).strip()

        # 根据描述判断这是否是结论步骤
        is_conclusion = False
        if isinstance(plan_list, list):
             # 检查当前执行的步骤（可能是最后一个“Done”或如果评估失败则为当前的“Pending”）是否是结论
             # 此逻辑是近似的 - 可能需要根据 LLM 处理状态更新的方式进行完善
             for item in reversed(plan_list): # Check recent items first
                 if isinstance(item, dict) and item.get('description') == "Conclusion":
                     # If Conclusion is Done or it's Pending and we are ending, consider it conclusion
                     if item.get('status') == "Done" or (item.get('status') == "Pending" and not exec_res.get("next_thought_needed", True)):
                         is_conclusion = True
                         break
                 # 简单检查，如果结论可能是子步骤，则可能需要嵌套搜索

        # 使用 is_conclusion 标志或 next_thought_needed 标志进行终止
        if not exec_res.get("next_thought_needed", True): # 主要终止信号
            shared["solution"] = dedented_thinking # 解决方案是最后一步的思考内容
            print(f"\nThought {thought_num} (Conclusion):")
            print(f"{textwrap.indent(dedented_thinking, '  ')}")
            print("\n最终计划状态：")
            print(textwrap.indent(plan_str_formatted, '  '))
            print("\n=== 最终解决方案 ===")
            print(dedented_thinking)
            print("======================\n")
            return "end"

        # 否则，继续链条
        print(f"\nThought {thought_num}:")
        print(f"{textwrap.indent(dedented_thinking, '  ')}")
        print("\n当前计划状态：")
        print(textwrap.indent(plan_str_formatted, '  '))
        print("-" * 50)

        return "continue"