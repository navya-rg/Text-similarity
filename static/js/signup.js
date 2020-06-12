$(document).ready(function(){


$("#signup").click(function(e){
e.preventDefault();
    var data1={};  // creating  a json object

var email_signup=$("#email_signup").val();
var branch=$("#branch").val();
var name=$("#name").val();
var regno=$("#regno").val();
var password=$("#password_signup").val();
var confpass=$("#pass_conf").val();
var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
if (name.length < 1) {
      toastr.info('name field cannot be empty!')
    }
    else if (regno.length < 1) {
      toastr.info(' Reg number field cannot be empty!')
    }
    else if(branch.length<1)
    {
       toastr.info('Enter a valid branch!')
    }
     else if (password.length < 1) {
      toastr.info(' Password field cannot be empty!')
    }
     else if (password!=confpass) {
      toastr.info('Retype the confirmed password correctly !')
    }

    else if (email_signup.length < 1) {
    toastr.info('Email can not be empty!')
    }

    else if(reg.test(email_signup) == false)
        {
             toastr.info('Enter valid email!')
        }
        else
        {
            $('#form_submit').submit();

    }

});

});