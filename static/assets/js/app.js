const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});


const optionMenu = document.querySelector(".select-menu"),
       selectBtn = optionMenu.querySelector(".select-btn"),
       options = optionMenu.querySelectorAll(".option"),
       sBtn_text = optionMenu.querySelector(".sBtn-text");

selectBtn.addEventListener("click", () => optionMenu.classList.toggle("active"));       

options.forEach(option =>{
    option.addEventListener("click", ()=>{
        let selectedOption = option.querySelector(".option-text").innerText;
        sBtn_text.innerText = selectedOption;

        optionMenu.classList.remove("active");
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const selectBtn = document.querySelector('.select-btn');
    const options = document.querySelectorAll('.option');
    const selectText = document.querySelector('.sBtn-text');
    const isSuperuserInput = document.getElementById('is_superuser');

    options.forEach(option => {
        option.addEventListener('click', () => {
            const value = option.getAttribute('data-value');
            const text = option.querySelector('.option-text').innerText;

            selectText.innerText = text;
            isSuperuserInput.value = value;
        });
    });
});