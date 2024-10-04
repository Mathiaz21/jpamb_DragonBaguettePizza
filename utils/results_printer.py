def print_results(analysis_results: dict) -> None:

  criteria: dict[str, str]  ={
    'assertion_error': 'assertion error',
    'no_error': 'ok',
    'infinite_loop': '*',
    'division_by_zero': 'divide by zero',
    'array_out_of_bounds': 'out of bounds',
    'null_pointer': 'null pointer',
  }

  for c in criteria:

    result_report = f'{c};{analysis_results[c] * 100}%'
    print(result_report)
