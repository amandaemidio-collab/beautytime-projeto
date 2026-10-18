// Edit teste aula record
query "teste_aula/{teste_aula_id}" verb=PATCH {
  api_group = "Event Logs"

  input {
    int teste_aula_id? filters=min:1
    dblink {
      table = "teste aula"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch "teste aula" {
      field_name = "id"
      field_value = $input.teste_aula_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $teste_aula
  }

  response = $teste_aula
  guid = "ReACWJbI6h-x0Q0y5axMkR6-9fo"
}