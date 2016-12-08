/**
 * SweetMates
 * login.js
 * 
 * The necessary JavaScript to prevent accidential form submits on login.html
 * 
 * Andrew Shackelford
 * ashackelford@college.harvard.edu
 * 
 * Eric Bornstein
 * ebornstein@college.harvard.edu
 * 
 * Catherine Tu
 * catherinetu@college.harvard.edu
 * 
 */

$(function(){ 
    // on DOM ready
    
    // disable submit button on load
    $('#submitbutton').attr('disabled','disabled');
    
    // when character pressed in field
    $('#username').bind('keyup', function() {
        // get lengths of fields
        var username_length = $("#username").val().length;
        var password_length = $("#password").val().length;
        if (username_length > 0 && password_length > 0) {
            // if all fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
    $('#password').bind('keyup', function() {
        // get lengths of fields
        var username_length = $("#username").val().length;
        var password_length = $("#password").val().length;
        if (username_length > 0 && password_length > 0) {
            // if all fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
});