export default {
    template: '#shoppinglist-component',
    data: function () {
        return {
            assetText: '',
            assetArr: [],
            fitText: '',
            fitArr: [],
            marketTypes: [],
            coveredList: [],
            neededList: [],
            substitutionNotes: [],
            fitMultiplier: 1,
            equivalentItems: []
        };
    },
    props: ['string'],
    created: function () {
        this.loadTypes();
        this.loadEquivalentItems();
    },
    mounted: function () {
    },
    watch: {
        fitMultiplier: function () {

            if (this.fitMultiplier == null)
                this.fitMultiplier = 1;

            this.calculateList();
        }
    },
    methods: {
        loadTypes: function () {

            var $that = this;
            $.getJSON('GetMarketTypes', null, function (data) {
                $that.marketTypes = data;
            });
        },
        loadEquivalentItems: function () {
            var $that = this;
            $.getJSON('GetItemEquivalences', null, function (data) {
                $that.equivalentItems = data;
            });
        },
        findEquivalentItem: function (fitItemId, assetArr) {
            // Check if this item has any equivalents
            if (!this.equivalentItems[fitItemId]) {
                return null;
            }

            // Get the list of equivalent item IDs
            var equivalentIds = this.equivalentItems[fitItemId];

            // Search for any equivalent item with available quantity in the asset list
            for (var i = 0; i < equivalentIds.length; i++) {
                var equivalentId = equivalentIds[i];
                var asset = _.find(assetArr, function (ass) {
                    return ass.id === equivalentId && ass.quantity > 0;
                });

                if (asset) {
                    return asset;
                }
            }

            return null;
        },
        // calculateTotalPrice: function () {
        //     var $that = this;
        //     var ids = _.map(this.resultTypes, function (t) { return t.id; }).join(',');

        //     $that.estimatedPrice = 0;

        //     var total = 0;
        //     $.getJSON('../Ship/GetBulkMarketTypePrice?marketTypeIDs=' + ids + '&_t=' + (new Date()).getTime(), null, function (data) {
        //         _.each(data, function (res) {
        //             var item = _.find($that.resultTypes, function (rt) { return rt.id = res.MarketTypeID; });
        //             total += (item.multiplier * res.Price);
        //         });

        //         $that.estimatedPrice = total;
        //     });
        // },
        onAssetInput: function (evt) {
            this.assetArr = parseFitText(this.assetText, this.marketTypes, true);
            this.calculateList();
        },
        onFitInput: function (evt) {
            this.fitArr = parseFitText(this.fitText, this.marketTypes, true);
            this.calculateList();
        },
        calculateList: function () {
            if (this.assetArr.length !== 0 && this.fitArr.length !== 0) {

                this.coveredList = [];
                this.neededList = [];
                this.substitutionNotes = [];

                var $that = this;

                // Create working copy of inventory
                var inventory = _.map(this.assetArr, function(asset) {
                    return {
                        id: asset.id,
                        name: asset.name,
                        quantity: asset.multiplier
                    };
                });

                // Track what's still needed for each requested item
                var requestedItems = _.map(this.fitArr, function(fit) {
                    return {
                        id: fit.id,
                        name: fit.name,
                        stillNeeded: fit.multiplier * $that.fitMultiplier
                    };
                });

                // PASS 1: Handle exact matches first
                _.each(requestedItems, function(request) {
                    if (request.stillNeeded <= 0) return;

                    var asset = _.find(inventory, function (item) {
                        return item.id == request.id;
                    });

                    if (asset) {
                        var quantityUsed = Math.min(request.stillNeeded, asset.quantity);

                        $that.coveredList.push({
                            id: request.id,
                            name: request.name,
                            quantity: quantityUsed
                        });

                        asset.quantity -= quantityUsed;
                        request.stillNeeded -= quantityUsed;
                    }
                });

                // PASS 2: Handle equivalent items for remaining needs
                _.each(requestedItems, function(request) {
                    while (request.stillNeeded > 0) {
                        var asset = $that.findEquivalentItem(request.id, inventory);

                        if (!asset) break;

                        var quantityUsed = Math.min(request.stillNeeded, asset.quantity);

                        $that.coveredList.push({
                            id: request.id,
                            name: asset.name,
                            quantity: quantityUsed
                        });

                        $that.substitutionNotes.push({
                            note: request.name + ' -> ' + asset.name,
                            quantity: quantityUsed
                        });

                        asset.quantity -= quantityUsed;
                        request.stillNeeded -= quantityUsed;
                    }
                });

                // PASS 3: Collect items still needed
                _.each(requestedItems, function(request) {
                    if (request.stillNeeded > 0) {
                        $that.neededList.push({
                            id: request.id,
                            name: request.name,
                            quantity: request.stillNeeded
                        });
                    }
                });
            }
        },
        addCommas: function (num) {
            return numeral(num).format('0,0');
        },
        copyToClipboard: function (text) {
            navigator.clipboard.writeText(text);
        },
    },
    computed: {
        groupedSubstitutionNotes: function() {
            var grouped = {};

            _.each(this.substitutionNotes, function(item) {
                if (!grouped[item.note]) {
                    grouped[item.note] = 0;
                }
                grouped[item.note] += item.quantity;
            });

            return _.map(grouped, function(quantity, note) {
                return quantity > 1 ? note + ' x' + quantity : note;
            });
        },
        coveredListText: function() {
            if (this.coveredList.length === 0) {
                return 'No items covered yet';
            }
            return _.map(this.coveredList, function(item) {
                return item.name + ' x' + item.quantity;
            }).join('\n');
        },
        neededListText: function() {
            if (this.neededList.length === 0) {
                return 'No items needed';
            }
            return _.map(this.neededList, function(item) {
                return item.name + ' x' + item.quantity;
            }).join('\n');
        },
        formattedSubstitutionNotes: function() {
            return _.map(this.groupedSubstitutionNotes, function(note) {
                return note.replace(' -> ', ' <b>-></b> ');
            });
        }
    }
}