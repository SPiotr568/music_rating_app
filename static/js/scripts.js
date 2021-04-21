function clock(){
    var date = new Date();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();

    if (minutes<10) minutes="0" + minutes;
    if (seconds<10) seconds="0" + seconds;

    var footer = document.getElementById("footer");
    footer.innerHTML = "&copy; 2021 PS | " +hours+":"+minutes+":"+seconds;
}

function rangeSlide(value) {
    document.getElementById('rangeValue').innerHTML = value;
}
