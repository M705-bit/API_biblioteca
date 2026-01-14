async function criarUsuario(){
    const idade = document.getElementById("idade").value;

    if (!idade){
        alert("Digite a sua idade!");
        return;
    }
    try {
        const response = await fetch("http://127.0.0.1:8000/users", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body:JSON.stringify({
                Age: idade
            })
        });
        if (!response.ok) {
            throw new Error(`Erro: ${response.status}`);
        }
        const data = await response.json();
        document.getElementById("resposta").innerText = data.message + " (ID: " + data.user_id + ")";
       
    setTimeout(() => {
        goToLoginPage();
    }, 2000);
       
    } catch (error) {
        alert("Erro ao criar usuário: " + error.message);
    }
}

async function login(){
    const id = document.getElementById("ID").value;

    if (!id){
        alert("Digite o seu ID!");
        return;
    }
    try {
        const response = await fetch(`http://127.0.0.1:8000/users/${id}/books`);
        
        if (!response.ok) {
            throw new Error(`Erro: ${response.status}`);
        }
        const data = await response.json();
        alert("Login bem-sucedido! Bem-vindo, " + data.name);
    } catch (error) {
        alert("Erro ao fazer login: " + error.message);
    }
}

async function goToLoginPage() {
    window.location.href = "/login";
}

