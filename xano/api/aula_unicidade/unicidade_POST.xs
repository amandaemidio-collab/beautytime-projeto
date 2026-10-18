// Add Unicidade record
query unicidade verb=POST {
  api_group = "aula unicidade"

  input {
    dblink {
      table = "Unicidade"
    }
  }

  stack {
    db.add Unicidade {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $unicidade
  }

  response = $unicidade
  guid = "u7cBHsj9wRA90cUPWjHDUL8g4HQ"
}