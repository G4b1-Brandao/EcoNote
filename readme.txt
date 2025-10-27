1 -	Baixe o Python 3.11.4
2 - 	Isntale o python 3.11.4 marque a opção para adicionar ao Path
	Marque a opção de ativar o python launcher pra todos os usuários (caso não tenha feito ainda em outra versão do python)

3 - 	na raiz do projeto. Execute:

	py -3.11 -m venv venv 		#Cria a Venv
	.\venv\Scripts\Activate.ps1   	#Ativa a venv no PowerShell

	observação: (Caso dê problema ao ativar a venv rode):
	Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
	.\venv\Scripts\Activate.ps1

	pip install			#instala as dependências na venv

Cuidados:

Sempre que adicionar uma nova dependência rode:

pip freeze > requirements.txt

para atualizar o requirements com a nova dependência
