from .drug import Drug

class Shelf:
    """
    OVERVIEW:
        Shelf is the primary manipulation object to utilize and employ drug objects. 
        Enables optional capacity that dictates the amount of drugs capable of being
        fit on the shelf. Prevents redundancy of drugs by identifying identical names
        and preventing addition of same drugs. Enables adding and removing drugs from 
        shelf structure. Enables collection of shelf statistics about total fields, 
        risk score, and other total drug statistics.

        This is designed to be useful for individuals storing medicine in their homes,
        pharmacists keeping track of SKUs and inventory from FDA approved drugs, and 
        to provide a malleable data manipulation object for implementation.
    ATTRIBUTES:
        corelist (list): a list containing all the individual drug items on the shelf.
        capacity (int): total capacity of the shelf (number of drugs) not to be exceeded

    USAGE EXAMPLE:
        >>> my_shelf = Shelf(capacity=20)
        >>> my_shelf.add_drug(Advil) # 1 drug shelf
        >>> my_shelf.add_drug(Oxycodone) # 2 drug shelf
        >>> my_shelf.remove_drug(Oxycodone.get_name()) # removes based on exact name match
        >>> # my_shelf has 1 drug
        >>> my_shelf.shelf_stats() # returns the basic descriptive stats for the shelf
    """
    def __init__(self, capacity: int = 10000):
        """
        OVERVIEW:
            Initializes shelf class object by defining the empty corelist and setting the 
            capacity of the shelf
            
        PARAMETERS:
            capacity (int): total maximum integer value of items available to place on shelf
                # default value of 10,000
        RETURN VALUE:
            None

        USAGE EXAMPLE:
            >>> my_shelf = Shelf(capacity=20) # initializes shelf object
        """
        # check capacity values
        if isinstance(capacity, bool):
            raise TypeError("capacity must be an integer, not a boolean")
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 1:
            raise ValueError("capacity must be at least 1")

        # initialize attributes
        self.corelist = []
        self.capacity = capacity

    def get_drugs(self):
        """
        OVERVIEW:
            Function returns list of all drugs on the shelf

        PARAMETERS:
            None

        RETURN VALUE:
            corelist (list): list of all drugs on the shelf

        USAGE EXAMPLE:
            >>> my_shelf.get_drugs() # returns list of drugs
        """
        # simply get the corelist of the shelf
        return self.corelist.copy()
        
    def add_drug (self, drug):
        """
        OVERVIEW:
            Function to add a drug to the shelf. Function has a couple of checks; it first 
            ensures that the drug is not already on the list by get_name function, and also
            ensures that the list is not capacity backed up. After doing so, the function 
            adds the drug to the list.
            
        PARAMETERS:
            drug (Drug): drug to be considered for addition to the list
            
        RETURN VALUE:
            None: simply adds drug to the list
            
        USAGE EXAMPLE:
            >>> my_shelf = Shelf(capacity=20) # initializes shelf object
            >>> my_shelf.add_drug(Advil) # adds advil to the shelf if space/not redundant
        """

        # check that drug is a drug and has a name
        if not isinstance(drug, Drug):
            raise TypeError("Please input a Drug to check for parameters")
        if drug.get_name() is None:
            raise ValueError("Cannot add drug without a name")

        # check for redundancies with existing shelf
        for item in self.corelist:
            if drug.get_name() == item.get_name():
                raise ValueError("Redundant - Drug already in the list")
                
        # check for capacity constraints
        if len(self.corelist) >= self.capacity:
            raise ValueError("Shelf is full")

        # add to list if all checks above go through
        self.corelist.append(drug)
        
    def remove_drug (self, name: str):
        """
        OVERVIEW:
            Function to remove drug from shelf. Takes in string with name of drug and checks
            entire shelf to see if matching name can be withdrawn. If matching name appears, 
            drug is removed from the list.
            
        PARAMETERS:
            name (str): result of Drug.get_name() for drug desired to be removed

        RETURN VALUE:
            None

        USAGE EXAMPLE:
            >>> my_shelf #imagine this is a shelf that has multiple drugs including advil
            >>> my_shelf.remove_drug("Advil") # checks get_name for all drugs and removes "Advil"
        """
        # check if we have a string to check
        if not isinstance(name, str):
            raise TypeError("Please input a string with the name of a drug to check for drugs to remove")

        # iterate through corelist and look for equivalent name to remove
        for item in self.corelist:
            if name == item.get_name():
                self.corelist.remove(item)
                return # terminate once found

        # error if not found
        raise ValueError(f"Drug '{name}' not found on shelf")
    
    def shelf_stats(self):
        """
        OVERVIEW:
            Provides statistics on the shelf, including newest drug, average 
            risk score, average total fields in drug_comprehensive, and percentage_full of
            the capacity of the shelf in terms of drug count.

        PARAMETERS:
            None

        RETURN VALUE:
            shelf_stats (dict): dictionary with 4 key shelf statistics

        USAGE EXAMPLE:
            >>> my_shelf.shelf_stats() # returns shelf stats if computable for my shelf
        """
        # ensure that corelist is populated
        if not self.corelist:
            return {
                "newest_drug": None,
                "average_risk_score": None,
                "average_total_fields": None,
                "percentage_full": 0
            }

        # define baseline parameters for newest_drug
        newest_drug = None
        newest_date = None
        total_risk_score = 0
        total_fields_count = 0

        # iterate through list to look
        for drug in self.corelist:
            drug_date = drug.get_date()
            if drug_date is not None:
                if newest_date is None or drug_date > newest_date:
                    newest_date = drug_date
                    newest_drug = [drug.get_name(), newest_date]
            total_risk_score += drug.risk_score()[1]
            comprehensive_data = drug.drug_comprehensive()
            total_fields_count += len(comprehensive_data)

        # calculate summary statistics
        num_drugs = len(self.corelist)
        average_risk_score = total_risk_score / num_drugs
        average_total_fields = total_fields_count / num_drugs
        percentage_full = len(self.corelist)/self.capacity

        # return final values
        return {
            "newest_drug": newest_drug,
            "average_risk_score": average_risk_score,
            "average_total_fields": average_total_fields,
            "percentage_full": percentage_full
        }
                