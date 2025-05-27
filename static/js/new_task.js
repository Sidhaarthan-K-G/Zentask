document.addEventListener('DOMContentLoaded',function(){
    const dateinput= document.getElementById('date');
    const today=new Date().toISOString().split('T')[0];
    dateinput.setAttribute('min',today)
})