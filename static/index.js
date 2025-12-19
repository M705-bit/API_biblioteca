document.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', function() {
        if (this.textContent === 'criar conta') {
            //window.location.href = '/criar_conta.html';
            alert('Você quer criar uma conta!');
        }
        else if (this.textContent === 'login') {
            //window.location.href = '/login.html';
            alert('Você quer fazer login!');
        }
    });
});
