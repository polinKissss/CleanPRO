const burger = document.querySelector('.burger');
const nav = document.querySelector('.main-nav');

if (burger && nav) {
    burger.addEventListener('click', () => {
        const open = nav.classList.toggle('is-open');
        burger.setAttribute('aria-expanded', open);
    });
}
