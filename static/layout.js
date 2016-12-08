/**
 * SweetMates
 * layout.js
 * 
 * The necessary JavaScript for sidebar animations using layout.html
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
    
    // when top part of sidebar clicked
    $('.demo2').on('click', function() {
        // switch that part's icon
        $('.glyphdemo2').toggleClass('glyphicon-menu-down glyphicon-menu-up');
    });
    // when middle part of sidebar clicked
    $('.demo3').on('click', function() {
        // switch that part's icon
        $('.glyphdemo3').toggleClass('glyphicon-menu-down glyphicon-menu-up');
    });
    // when bottom part of sidebar clicked
    $('.demo4').on('click', function() {
        // switch that part's icon
        $('.glyphdemo4').toggleClass('glyphicon-menu-down glyphicon-menu-up');
    });
});