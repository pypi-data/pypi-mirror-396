# pydantic-config-generator

**pydantic-config-generator** è una libreria Python che fornisce prompt interattivi per la configurazione di modelli Pydantic. Permette di creare interfacce CLI interattive per raccogliere e validare dati secondo i tuoi modelli Pydantic.

## Caratteristiche

- 🎯 **Validazione automatica**: Usa la validazione di Pydantic per garantire dati corretti
- 🔄 **Supporto per modelli annidati**: Gestisce configurazioni complesse con modelli Pydantic annidati
- ⚡ **Facile da usare**: Basta passare il tuo modello Pydantic e pydantic-config-generator fa il resto
- 🛡️ **Type-safe**: Sfrutta il sistema di tipi di Pydantic
- 💾 **Salvataggio in file**: Salva le configurazioni in formato INI o .env per un uso successivo

## Installazione

```bash
pip install pydantic-config-generator
```

## Utilizzo

### Esempio Base

```python
from pydantic import BaseModel
from pydantic_config_generator import prompt

class ExampleConfig(BaseModel):
    name: str = ''
    surname: str
    age: int
    is_student: bool = True

# Avvia il prompt interattivo
# prompt() restituisce un dizionario con i valori inseriti
config_data = prompt(ExampleConfig)
```

### Esempio con Modelli Annidati

```python
from pydantic import BaseModel
from pydantic_config_generator import prompt

class ExampleSubConfig(BaseModel):
    name: str
    surname: str
    age: int

class ExampleConfig(BaseModel):
    name: str = ''
    surname: str
    age: int
    is_student: bool = True
    teacher: ExampleSubConfig = None

# prompt() restituisce un dizionario
config_data = prompt(ExampleConfig)
```

Il sistema ti chiederà di inserire i valori per ogni campo, mostrando i valori di default tra parentesi quadre. I campi obbligatori devono essere compilati, mentre quelli opzionali possono essere saltati. Se lasci un campo vuoto e ha un valore di default, verrà utilizzato il valore di default. La funzione `prompt()` restituisce un dizionario Python con i dati inseriti.

### Salvare la Configurazione in un File

Dopo aver raccolto la configurazione tramite `prompt()`, puoi salvarla in diversi formati:

#### Salvataggio in formato INI

```python
from pydantic import BaseModel
from pydantic_config_generator import prompt, write_ini

class ExampleConfig(BaseModel):
    name: str = ''
    surname: str
    age: int
    is_student: bool = True

# Raccogli la configurazione (restituisce un dizionario)
config_data = prompt(ExampleConfig)

# Salva in un file INI
# write_ini() accetta un dizionario, non un'istanza BaseModel
write_ini(config_data, 'config.ini')
```

La funzione `write_ini()` crea un file INI dove ogni chiave del dizionario diventa una sezione. I modelli annidati vengono salvati come sezioni separate.

#### Salvataggio in formato .env

```python
from pydantic import BaseModel
from pydantic_config_generator import prompt, write_env

class ExampleConfig(BaseModel):
    name: str = ''
    surname: str
    age: int
    is_student: bool = True

# Raccogli la configurazione (restituisce un dizionario)
config_data = prompt(ExampleConfig)

# Salva in un file .env
# write_env() accetta un dizionario, non un'istanza BaseModel
write_env(config_data, '.env', group_separator='_', use_uppercase=True)
```

La funzione `write_env()` supporta i seguenti parametri:
- `file`: nome del file (default: `.env`)
- `group_separator`: separatore per i gruppi annidati (default: `.`)
- `use_uppercase`: se usare lettere maiuscole per i nomi delle variabili (default: `True`)

#### Funzioni di convenienza

Puoi anche combinare prompt e salvataggio in un'unica chiamata:

```python
from pydantic import BaseModel
from pydantic_config_generator import create_ini, create_env

class ExampleConfig(BaseModel):
    name: str = ''
    surname: str
    age: int
    is_student: bool = True

# Crea e salva direttamente in formato INI
create_ini(ExampleConfig, 'config.ini')

# Crea e salva direttamente in formato .env
create_env(ExampleConfig, '.env', group_separator='_', use_uppercase=True)
```

Se il file esiste già, ti verrà chiesta conferma prima di sovrascriverlo.

## Come Funziona

1. **Campi semplici**: Per ogni campo del modello, pydantic-config-generator chiede un valore, mostrando il default se disponibile
2. **Validazione**: Ogni input viene validato secondo le regole del modello Pydantic
3. **Modelli annidati**: Se un campo è un modello Pydantic, pydantic-config-generator chiede se includerlo (se opzionale) e poi richiede i suoi campi
4. **Gestione errori**: Se un valore non è valido, viene mostrato un errore e viene richiesto di nuovo
5. **Salvataggio in file**: 
   - `prompt()` restituisce un dizionario Python con i dati inseriti
   - `write_ini()` accetta un dizionario e salva la configurazione in formato INI, dove ogni chiave del dizionario diventa una sezione
   - `write_env()` accetta un dizionario e salva la configurazione in formato .env, con supporto per modelli annidati tramite separatori personalizzabili
   - `create_ini()` e `create_env()` combinano prompt e salvataggio in un'unica operazione

## Requisiti

- Python >= 3.7
- pydantic >= 1.0, < 2.0

## Licenza

MIT License

## Contribuire

I contributi sono benvenuti! Sentiti libero di aprire issue o pull request.

