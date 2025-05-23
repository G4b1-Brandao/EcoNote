function moverMenu(distMenu, distBody) {
    $('.menu').animate({
        left: distMenu + "px"
    }, 200);
    $('body').animate({
        left: distBody + "px"
    }, 200);
}
$(document).ready(() => {
    $('.icon-menu').click(() => { moverMenu(0, 350) });
    $('.icon-close').click(() => { moverMenu(-350, 0) });
});