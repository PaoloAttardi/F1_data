function newForm() {
    var form = document.getElementById('Type').value;
    if (form == 'Race') {
        var myOpts = document.getElementById('FirstDriver').options;
        var drivers = [];
        for (let i = 1; i < myOpts.length; i++) {
            var str = '<option value=' + myOpts[i].value + '>' + myOpts[i].value + '</option>';
            drivers.push(str);
        }
        document.getElementById("select").innerHTML =
            `<div class="col"><select class="form-control" id="ThirdDriver" name="ThirdDriver" required><option value="" selected disabled>Third Driver Number</option>${drivers}</select></div><div class="col"><select class="form-control" id="FourthDriver" name="FourthDriver" required><option value="" selected disabled>Fourth Driver Number</option>${drivers}</select></div>`;
    }
}