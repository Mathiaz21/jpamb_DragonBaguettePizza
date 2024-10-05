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

    result_percentage: int = int( analysis_results*100 )
    result_report = f'{c};{result_percentage}%'
    print(result_report)
