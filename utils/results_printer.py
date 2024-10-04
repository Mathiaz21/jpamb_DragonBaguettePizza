def print_results(analysis_results: dict) -> None:

  criteria: list[str]  =[
    'assertion error',
    'ok',
    '*',
    'divide by zero',
    'out of bounds',
    'null pointer',
  ]

  for c in criteria:

    result_report = f'{c};{analysis_results[c] * 100}%'
    print(result_report)