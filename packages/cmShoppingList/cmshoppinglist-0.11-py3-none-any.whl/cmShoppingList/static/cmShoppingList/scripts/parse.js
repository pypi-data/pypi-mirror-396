_.mixin({
  clean: function(str) {
    return _.trim(str).replace(/\s+/g, ' ');
  }
});

function parseFitText(text, marketLookup, includeHull) {
    var names = text.split('\n');

    var idList = "";
    var fitItems = [];

    var eftMode = false;

    _.each(names, function (name) {

        // trim leading and trailing whitespace on the line and multiple spaces to one space
        var items = name.split('\t');

        // if items not seven then clean, otherwise keep cause this is asset view
        if (items.length != 7) {
            name = name.replace(/\t/g, ' ');
            name = _.clean(name);
        }

        var num = null;

        var subNames = name.split(','); // case where multiple items on one line

        // check for eft mode
        if (name.charAt(0) == '[') {
            eftMode = true;

            if (includeHull) {
                var type = name.substring(0, name.indexOf(',')).replace('[', '');

                if (marketLookup instanceof Array) {
                    var item = _.find(marketLookup, function (obj) { return (obj.text == type || obj.name == type); });

                    if(item != null)
                        fitItems.push({ name: item.name, id: item.id, multiplier: 1 });
                }
            }

            return;
        }

        if (eftMode && subNames.length > 1) {
            // process and add items here then return
            _.each(subNames, function (subName) {
                subName = _.clean(subName);

                if (marketLookup instanceof Array) {
                    var subItem = _.find(marketLookup, function (obj) { return (obj.text == subName || obj.name == subName) });

                    if (subItem != null) {

                        // if already in list increment
                        var fItem = _.find(fitItems, function (item) { return item.id == subItem.id; });

                        // if exists increment
                        if (fItem != null)
                            fItem.multiplier = fItem.multiplier + 1;
                        else
                            fitItems.push({ name: subName, id: subItem.id, multiplier: 1 });
                    }
                }
                else {
                    var subItem = $(marketLookup).find('option').filter(function () { return $(this).text() == subName; });
                    if (subItem.length == 1) {
                        var id = $(subItem).val();
                        fitItems.push({ name: subName, id: id, multiplier: num });
                    }
                }
            });

            return;
        }
        else if (items.length == 7) {
            name = _.clean(items[0]);
            num = parseInt(items[1]);
        }
        else if (eftMode) {

            var regex = / x\d+$/;
            var res = name.match(regex);
            var num = 1; // default multiplier

            if (res != null && res.length == 1) { // check if has multiplier, otherwise just use name
                name = name.replace(res[0], '');
                num = parseInt(res[0].replace('x', '').replace(' ', '')); // this is to get the multiplier
            }
        }
        else {

            // match pre-number
            var num = 1; // default multiplier

            var res = name.match(/^\d*[,]?\d+x /);

            // if no number don't find and add
            if (res != null && res.length == 1) {
                name = name.replace(res[0], '');
                name = _.clean(name);
                num = parseInt(res[0].replace(/,/g, '').replace('x ', '')); // this is to get the multiplier
            }

            // if not found check for multipler at the end
            if (res == null || res.length == 0) {
                res = name.match(/ \d*[,]?\d+$/);

                if (res != null && res.length == 1) {
                    name = name.replace(res[0], '');
                    name = _.clean(name);
                    num = parseInt(res[0].replace(' ', '')); // this is to get the multiplier
                }
            }

            // check for eft line
            if (res == null || res.length == 0) {
                var regex = / x\d+$/;
                res = name.match(regex);

                if (res != null && res.length == 1) { // check if has multiplier, otherwise just use name
                    name = name.replace(res[0], '');
                    num = parseInt(res[0].replace('x', '').replace(' ', '')); // this is to get the multiplier
                }
            }
        }

        if (marketLookup instanceof Array) {
            var subItem = _.find(marketLookup, function (obj) { return (obj.text == name || obj.name == name); });

            if (subItem != null) {

                // if already in list increment
                var fItem = _.find(fitItems, function (item) { return item.id == subItem.id; });

                // if exists increment
                if (fItem != null)
                    fItem.multiplier = (fItem.multiplier + num);
                else
                    fitItems.push({ name: name, id: subItem.id, multiplier: num });
            }
        }
        else {
            var item = $(marketLookup).find('option').filter(function () { return $(this).text() == name; });
            if (item.length == 1 && num != null) {
                var id = $(item).val();
                var itemName = $(item).text();

                // if already in list increment
                var fItem = _.find(fitItems, function (item) { return item.id == id; });

                // if exists increment
                if (fItem != null)
                    fItem.multiplier = fItem.multiplier + num;
                else
                    fitItems.push({ name: name, id: id, multiplier: num });

            }
        }

    });

    return fitItems;
}

