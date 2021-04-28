$(document).ready(function(){

    var send = {
        productId:'6',
        quantity:'2'
    };

    $.ajax({ 
        type:"POST",
        url:"/addToCart",
        data: JSON.stringify(send),
        dataType: "json",
        contentType: 'application/json'
    });  
});