$(document).ready(function(){


$("#login").click(function(){

var data={};
var email_login=$('#login_email').val();  
var password_login=$("#login_password").val();
data['email_login']=email_login;
data['password_login']=password_login;  //creating an array

 data = JSON.stringify(data);       //creating the array into a Json string
        console.log(data);
        $.ajax({
            type: "POST",
            async: false,
            url: "php/login.php",
            data: {
                'mydata': data,
            },
            success: function(result) {
                console.log(result);
                result = result.trim();
                result = result.substring(1, result.length - 1);
                result = JSON.parse(result);
                if (result.msg == "logged in") {
                     toastr.success('Successfully logged in');
                     window.location.href = "index.html";
                   
                }
                else{
                    toastr.info('Invalid email/password');
                }
            }
        });

});

})