// Edit Unicidade record
query "unicidade/{unicidade_id}" verb=PATCH {
  api_group = "aula unicidade"

  input {
    int unicidade_id? filters=min:1
    dblink {
      table = "Unicidade"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch Unicidade {
      field_name = "id"
      field_value = $input.unicidade_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $unicidade
  }

  response = $unicidade
  guid = "vLuwBfhudfMYhrMn9Feb3xGdAd8"
}