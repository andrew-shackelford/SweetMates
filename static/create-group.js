/**
 * SweetMates
 * create-group.js
 * 
 * The necessary JavaScript to prevent accidential form submits on create-group.html
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
    
    // when character pressed in groupname field
    $('#groupname').bind('keyup', function() {
        // get lengths of fields
        var group_name_length = $("#groupname").val().length;
        var group_code_length = $("#groupcode").val().length;
        if (group_name_length > 0 && group_code_length > 0) {
            // if both fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
    
    // when character pressed in groupcode field
    $('#groupcode').bind('keyup', function() {
        // get lengths of fields
        var group_name_length = $("#groupname").val().length;
        var group_code_length = $("#groupcode").val().length;
        if (group_name_length > 0 && group_code_length > 0) {
            // if both fields filled, enable button
            $('#submitbutton').removeAttr('disabled');
        } else {
            // otherwise, disable button
            $('#submitbutton').attr('disabled','disabled');
        }
    });
    
});