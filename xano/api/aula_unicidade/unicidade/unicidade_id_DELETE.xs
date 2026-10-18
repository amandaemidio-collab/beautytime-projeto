// Delete Unicidade record.
query "unicidade/{unicidade_id}" verb=DELETE {
  api_group = "aula unicidade"

  input {
    int unicidade_id? filters=min:1
  }

  stack {
    db.del Unicidade {
      field_name = "id"
      field_value = $input.unicidade_id
    }
  }

  response = null
  guid = "OYdywzKnK6HNgH-jlrgzeHQeCl0"
}