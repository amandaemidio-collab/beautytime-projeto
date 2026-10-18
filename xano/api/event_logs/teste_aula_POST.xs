// Add teste aula record
query teste_aula verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = "teste aula"
    }
  }

  stack {
    db.add "teste aula" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $teste_aula
  }

  response = $teste_aula
  guid = "uxBrcL_YXlTWII1xA4y5ouR4w0g"
}