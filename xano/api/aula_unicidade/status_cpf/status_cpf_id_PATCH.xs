// Edit STATUS_CPF record
query "status_cpf/{status_cpf_id}" verb=PATCH {
  api_group = "aula unicidade"

  input {
    int status_cpf_id? filters=min:1
    dblink {
      table = "STATUS_CPF"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch STATUS_CPF {
      field_name = "id"
      field_value = $input.status_cpf_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $status_cpf
  }

  response = $status_cpf
  guid = "j8vmCn1StG64dfYaENOdjltrcdo"
}