from zope.schema import Choice

from wise.content.search import db, sql
from z3c.form.field import Fields

from .base import (EmbededForm, ItemDisplay, MarineUnitIDSelectForm,
                   MultiItemDisplayForm)
from .utils import (data_to_xls, register_form, register_form_section,
                    register_subform)
from .vocabulary import SubFormsVocabulary


@register_form
class A81bForm(EmbededForm):
    """ Main form for A81b.

    Allows selecting between Extraction of fish, seaweed, etc
    """

    title = 'Article 8.1b (Analysis of pressure impacts)'

    @property
    def fields(self):
        # TODO: could this be reimplemented with simple vocab?
        vocab = SubFormsVocabulary(self.__class__)
        theme = Choice(
            __name__='theme',
            title=u"Select theme",
            required=False,
            vocabulary=vocab,
        )

        return Fields(theme)

    def default_theme(self):

        field = self.fields['theme']
        vocab = field.field.vocabulary
        value = vocab._terms[0].value

        return value

    def get_subform(self):
        klass = self.data.get('theme')

        return super(A81bForm, self).get_subform(klass)


# region Extraction of fish and shellfish
class A81bExtractionFishItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bExtractionFishShellfish
    order_field = 'MSFD8b_ExtractionFishShellfish_ID'


@register_subform(A81bForm)
class A81bExtractionFishSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Extraction of fish and shellfish'
    mapper_class = sql.MSFD8bExtractionFishShellfish

    def get_subform(self):
        return A81bExtractionFishItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bExtractionFishItemDisplay)
class A81bExtractionFishAssessment(ItemDisplay):
    title = 'Asessment of extraction of fish and shellfish'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bExtractionFishShellfishAssesment,
                'MSFD8b_ExtractionFishShellfish',
                self.context.item.MSFD8b_ExtractionFishShellfish_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bExtractionFishShellfishAssesmentIndicator,
            'MSFD8b_ExtractionFishShellfish_Assesment',
            self.item.MSFD8b_ExtractionFishShellfish_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO
# MSFD8bExtractionFishShellfishActivity is not directly related to
# MSFD8b_ExtractionFishShellfish table
# needs to be joined with MSFD8bExtractionFishShellfishActivityDescription
# table first
@register_form_section(A81bExtractionFishItemDisplay)
class A81bExtractionFishActivities(ItemDisplay):
    title = 'Activities producing extraction of fish and shellfish'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bExtractionFishShellfishActivity,
                sql.MSFD8bExtractionFishShellfishActivityDescription,
                'MSFD8b_ExtractionFishShellfish',
                self.context.item.MSFD8b_ExtractionFishShellfish_ID
            )


@register_form_section(A81bExtractionFishItemDisplay)
class A81bExtractionFishImpacts(ItemDisplay):
    title = 'Impacts produced by the extraction of fish and shellfish'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bExtractionFishShellfishSumInfo2ImpactedElement,
                'MSFD8b_ExtractionFishShellfish',
                self.context.item.MSFD8b_ExtractionFishShellfish_ID
            )
# endregion Extraction of fish and shellfish


# region Extraction of seaweed, maerl and other
class A81bExtractionSeaweedItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bExtractionSeaweedMaerlOther
    order_field = 'MSFD8b_ExtractionSeaweedMaerlOther_ID'


@register_subform(A81bForm)
class A81bExtractionSeaweedSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Extraction of seaweed, maerl and other'
    mapper_class = sql.MSFD8bExtractionSeaweedMaerlOther

    def get_subform(self):
        return A81bExtractionSeaweedItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bExtractionSeaweedItemDisplay)
class A81bExtractionSeaweedAssessment(ItemDisplay):
    title = 'Asessment of extraction of seaweed, maerl and other'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bExtractionSeaweedMaerlOtherAssesment,
                'MSFD8b_ExtractionSeaweedMaerlOther',
                self.context.item.MSFD8b_ExtractionSeaweedMaerlOther_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bExtractionSeaweedMaerlOtherAssesmentIndicator,
            'MSFD8b_ExtractionSeaweedMaerlOther_Assesment',
            self.item.MSFD8b_ExtractionSeaweedMaerlOther_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]

# TODO
# MSFD8bExtractionSeaweedMaerlOtherActivity is not directly related to
# MSFD8b_ExtractionSeaweedMaerlOther table
# needs to be joined with MSFD8bExtractionSeaweedMaerlOtherActivityDescription
# table first
@register_form_section(A81bExtractionSeaweedItemDisplay)
class A81bExtractionSeaweedActivities(ItemDisplay):
    title = 'Activities producing extraction of seaweed, maerl and other'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bExtractionSeaweedMaerlOtherActivity,
                sql.MSFD8bExtractionSeaweedMaerlOtherActivityDescription,
                'MSFD8b_ExtractionSeaweedMaerlOther',
                self.context.item.MSFD8b_ExtractionSeaweedMaerlOther_ID
            )


@register_form_section(A81bExtractionSeaweedItemDisplay)
class A81bExtractionSeaweedImpacts(ItemDisplay):
    title = 'Impacts produced by the extraction of seaweed, maerl and other'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bExtractionSeaweedMaerlOtherSumInfo2ImpactedElement,
                'MSFD8b_ExtractionSeaweedMaerlOther',
                self.context.item.MSFD8b_ExtractionSeaweedMaerlOther_ID
            )
# endregion Extraction of seaweed, maerl and other


# region Hazardous substances
class A81bHazardousItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bHazardousSubstance
    order_field = 'MSFD8b_HazardousSubstances_ID'


@register_subform(A81bForm)
class A81bHazardousSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Hazardous substances'
    mapper_class = sql.MSFD8bHazardousSubstance

    def get_subform(self):
        return A81bHazardousItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bHazardousItemDisplay)
class A81bHazardousAssessment(ItemDisplay):
    title = 'Asessment of hazardous substances'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bHazardousSubstancesAssesment,
                'MSFD8b_HazardousSubstances',
                self.context.item.MSFD8b_HazardousSubstances_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bHazardousSubstancesAssesmentIndicator,
            'MSFD8b_HazardousSubstances_Assesment',
            self.item.MSFD8b_HazardousSubstances_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]

#  TODO
# MSFD8bHazardousSubstancesActivity is not directly related to
# MSFD8b_HazardousSubstances table
# needs to be joined with MSFD8bHazardousSubstancesActivityDescription table
# first
@register_form_section(A81bHazardousItemDisplay)
class A81bHazardousActivities(ItemDisplay):
    title = 'Activities producing hazardous substances'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bHazardousSubstancesActivity,
                sql.MSFD8bHazardousSubstancesActivityDescription,
                'MSFD8b_HazardousSubstances',
                self.context.item.MSFD8b_HazardousSubstances_ID
            )


@register_form_section(A81bHazardousItemDisplay)
class A81bHazardousImpacts(ItemDisplay):
    title = 'Impacts produced by the hazardous substances'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bHazardousSubstancesSumInfo2ImpactedElement,
                'MSFD8b_HazardousSubstances',
                self.context.item.MSFD8b_HazardousSubstances_ID
            )
# endregion Hazardous substances


# region Hydrological processes
class A81bHydroItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bHydrologicalProcess
    order_field = 'MSFD8b_HydrologicalProcesses_ID'


@register_subform(A81bForm)
class A81bHydroSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Hydrological processes'
    mapper_class = sql.MSFD8bHydrologicalProcess

    def get_subform(self):
        return A81bHydroItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bHydroItemDisplay)
class A81bHydroAssessment(ItemDisplay):
    title = 'Asessment of hydrological processes'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bHydrologicalProcessesAssesment,
                'MSFD8b_HydrologicalProcesses',
                self.context.item.MSFD8b_HydrologicalProcesses_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bHydrologicalProcessesAssesmentIndicator,
            'MSFD8b_HydrologicalProcesses_Assesment',
            self.item.MSFD8b_HydrologicalProcesses_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]

#  TODO
# MSFD8bHydrologicalProcessesActivity is not directly related to
# MSFD8b_HydrologicalProcesses table
# needs to be joined with MSFD8bHydrologicalProcessesActivityDescription table
# first
@register_form_section(A81bHydroItemDisplay)
class A81bHydroActivities(ItemDisplay):
    title = 'Activities producing hydrological processes'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bHydrologicalProcessesActivity,
                sql.MSFD8bHydrologicalProcessesActivityDescription,
                'MSFD8b_HydrologicalProcesses',
                self.context.item.MSFD8b_HydrologicalProcesses_ID
            )


@register_form_section(A81bHydroItemDisplay)
class A81bHydroImpacts(ItemDisplay):
    title = 'Impacts produced by the hydrological processes'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bHydrologicalProcessesSumInfo2ImpactedElement,
                'MSFD8b_HydrologicalProcesses',
                self.context.item.MSFD8b_HydrologicalProcesses_ID
            )
# endregion Hydrological processes


# region Marine litter
class A81bMarineLitterItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bLitter
    order_field = 'MSFD8b_Litter_ID'


@register_subform(A81bForm)
class A81bMarineLitterSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Marine litter'
    mapper_class = sql.MSFD8bLitter

    def get_subform(self):
        return A81bMarineLitterItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bMarineLitterItemDisplay)
class A81bMarineLitterAssessment(ItemDisplay):
    title = 'Asessment of marine litter'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bLitterAssesment,
                'MSFD8b_Litter',
                self.context.item.MSFD8b_Litter_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bLitterAssesmentIndicator,
            'MSFD8b_Litter_Assesment',
            self.item.MSFD8b_Litter_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]

#  TODO
# MSFD8bLitterActivity is not directly related to
# MSFD8b_Litter table
# needs to be joined with MSFD8bLitterActivityDescription table first
@register_form_section(A81bMarineLitterItemDisplay)
class A81bMarineLitterActivities(ItemDisplay):
    title = 'Activities producing marine litter'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bLitterActivity,
                sql.MSFD8bLitterActivityDescription,
                'MSFD8b_Litter',
                self.context.item.MSFD8b_Litter_ID
            )


@register_form_section(A81bMarineLitterItemDisplay)
class A81bMarineLitterImpacts(ItemDisplay):
    title = 'Impacts produced by the marine litter'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bLitterSumInfo2ImpactedElement,
                'MSFD8b_Litter',
                self.context.item.MSFD8b_Litter_ID
            )
# endregion Marine litter


# region Microbial pathogens
class A81bMicrobialItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bMicrobialPathogen
    order_field = 'MSFD8b_MicrobialPathogens_ID'


@register_subform(A81bForm)
class A81bMicrobialSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Microbial pathogens'
    mapper_class = sql.MSFD8bMicrobialPathogen

    def get_subform(self):
        return A81bMicrobialItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bMicrobialItemDisplay)
class A81bMicrobialAssessment(ItemDisplay):
    title = 'Asessment of microbial pathogens'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bMicrobialPathogensAssesment,
                'MSFD8b_MicrobialPathogens',
                self.context.item.MSFD8b_MicrobialPathogens_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bMicrobialPathogensAssesmentIndicator,
            'MSFD8b_MicrobialPathogens_Assesment',
            self.item.MSFD8b_MicrobialPathogens_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO
# MSFD8bMicrobialPathogensActivity is not directly related to
# MSFD8b_MicrobialPathogens table
# needs to be joined with MSFD8bMicrobialPathogensActivityDescription table first
@register_form_section(A81bMicrobialItemDisplay)
class A81bMicrobialActivities(ItemDisplay):
    title = 'Activities producing microbial pathogens'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bMicrobialPathogensActivity,
                sql.MSFD8bMicrobialPathogensActivityDescription,
                'MSFD8b_MicrobialPathogens',
                self.context.item.MSFD8b_MicrobialPathogens_ID
            )


# TODO
# missing table MSFD8bMicrobialPathogenSumInfo2ImpactedElement ??
# @register_form_section(A81bMicrobialItemDisplay)
# class A81bMicrobialImpacts(ItemDisplay):
#     title = 'Impacts produced by the microbial pathogens'
#
#     def get_db_results(self):
#         if self.context.item:
#             return db.get_related_record(
#                 sql.MSFD8bMicrobialPathogenSumInfo2ImpactedElement,
#                 'MSFD8b_MicrobialPathogens',
#                 self.context.item.MSFD8b_MicrobialPathogens_ID
#             )
# endregion Microbial pathogens


# region Non-indigenous species
class A81bNonIndigenousItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bNI
    order_field = 'MSFD8b_NIS_ID'


@register_subform(A81bForm)
class A81bNonIndigenousSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Non-indigenous species'
    mapper_class = sql.MSFD8bNI

    def get_subform(self):
        return A81bNonIndigenousItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bNonIndigenousItemDisplay)
class A81bNonIndigenousAssessment(ItemDisplay):
    title = 'Asessment of non-indigenous species'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bNISAssesment,
                'MSFD8b_NIS',
                self.context.item.MSFD8b_NIS_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bNISAssesmentIndicator,
            'MSFD8b_NIS_Assesment',
            self.item.MSFD8b_NIS_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO CHECK IF IMPLEMENTATION IS CORRECT
# MSFD8bNISActivity is not directly related to
# MSFD8b_NIS table
# needs to be joined with MSFD8bNISActivityDescription table first
@register_form_section(A81bNonIndigenousItemDisplay)
class A81bNonIndigenousActivities(ItemDisplay):
    title = 'Activities producing non-indigenous species'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bNISActivity,
                sql.MSFD8bNISActivityDescription,
                'MSFD8b_NIS',
                self.context.item.MSFD8b_NIS_ID
            )


@register_form_section(A81bNonIndigenousItemDisplay)
class A81bNonIndigenousImpacts(ItemDisplay):
    title = 'Impacts produced by non-indigenous species'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bNISSumInfo2ImpactedElement,
                'MSFD8b_NIS',
                self.context.item.MSFD8b_NIS_ID
            )
# endregion Non-indigenous species


# region Underwater noise
class A81bNoiseItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bNoise
    order_field = 'MSFD8b_Noise_ID'


@register_subform(A81bForm)
class A81bNonIndigenousSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Underwater noise'
    mapper_class = sql.MSFD8bNoise

    def get_subform(self):
        return A81bNoiseItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bNoiseItemDisplay)
class A81bNoiseAssessment(ItemDisplay):
    title = 'Asessment of underwater noise'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bNoiseAssesment,
                'MSFD8b_Noise',
                self.context.item.MSFD8b_Noise_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bNoiseAssesmentIndicator,
            'MSFD8b_Noise_Assesment',
            self.item.MSFD8b_Noise_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO CHECK IF IMPLEMENTATION IS CORRECT
@register_form_section(A81bNoiseItemDisplay)
class A81bNoiseActivities(ItemDisplay):
    title = 'Activities producing underwater noise'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bNoiseActivity,
                sql.MSFD8bNoiseActivityDescription,
                'MSFD8b_Noise',
                self.context.item.MSFD8b_Noise_ID
            )


@register_form_section(A81bNoiseItemDisplay)
class A81bNoiseImpacts(ItemDisplay):
    title = 'Impacts produced by underwater noise'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bNoiseSumInfo2ImpactedElement,
                'MSFD8b_Noise',
                self.context.item.MSFD8b_Noise_ID
            )
# endregion Underwater noise


# region Nutrients
class A81bNutrientItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bNutrient
    order_field = 'MSFD8b_Nutrients_ID'


@register_subform(A81bForm)
class A81bNutrientSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Nutrients'
    mapper_class = sql.MSFD8bNutrient

    def get_subform(self):
        return A81bNoiseItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bNutrientItemDisplay)
class A81bNutrientAssessment(ItemDisplay):
    title = 'Asessment of nutrients'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bNutrientsAssesment,
                'MSFD8b_Nutrients',
                self.context.item.MSFD8b_Nutrients_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bNutrientsAssesmentIndicator,
            'MSFD8b_Nutrients_Assesment',
            self.item.MSFD8b_Nutrients_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO CHECK IF IMPLEMENTATION IS CORRECT
@register_form_section(A81bNutrientItemDisplay)
class A81bNutrientActivities(ItemDisplay):
    title = 'Activities producing nutrients'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bNutrientsActivity,
                sql.MSFD8b_Nutrients_ActivityDescription,
                'MSFD8b_Nutrients',
                self.context.item.MSFD8b_Nutrients_ID
            )


@register_form_section(A81bNutrientItemDisplay)
class A81bNutrientImpacts(ItemDisplay):
    title = 'Impacts produced by the nutrients'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bNutrientsSumInfo2ImpactedElement,
                'MSFD8b_Nutrients',
                self.context.item.MSFD8b_Nutrients_ID
            )
# endregion Nutrients


# region Physical damage
class A81bPhysicalDamageItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bPhysicalDamage
    order_field = 'MSFD8b_PhysicalDamage_ID'


@register_subform(A81bForm)
class A81bPhysicalDamageSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Physical damage'
    mapper_class = sql.MSFD8bPhysicalDamage

    def get_subform(self):
        return A81bPhysicalDamageItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bPhysicalDamageItemDisplay)
class A81bPhysicalDamageAssessment(ItemDisplay):
    title = 'Asessment of physical damage'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bPhysicalDamageAssesment,
                'MSFD8b_PhysicalDamage',
                self.context.item.MSFD8b_PhysicalDamage_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bPhysicalDamageAssesmentIndicator,
            'MSFD8b_PhysicalDamage_Assesment',
            self.item.MSFD8b_PhysicalDamage_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO CHECK IF IMPLEMENTATION IS CORRECT
@register_form_section(A81bPhysicalDamageItemDisplay)
class A81bPhysicalDamageActivities(ItemDisplay):
    title = 'Activities producing physical damage'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bPhysicalDamageActivity,
                sql.MSFD8bPhysicalDamageActivityDescription,
                'MSFD8b_PhysicalDamage',
                self.context.item.MSFD8b_PhysicalDamage_ID
            )


@register_form_section(A81bPhysicalDamageItemDisplay)
class A81bPhysicalDamageImpacts(ItemDisplay):
    title = 'Impacts produced by the physical damage'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bPhysicalDamageSumInfo2ImpactedElement,
                'MSFD8b_PhysicalDamage',
                self.context.item.MSFD8b_PhysicalDamage_ID
            )
# endregion Physical damage


# region Physical loss
class A81bPhysicalLosItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bPhysicalLos
    order_field = 'MSFD8b_PhysicalLoss_ID'


@register_subform(A81bForm)
class A81bPhysicalLosSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Physical loss'
    mapper_class = sql.MSFD8bPhysicalLos

    def get_subform(self):
        return A81bPhysicalLosItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bPhysicalLosItemDisplay)
class A81bPhysicalLosAssessment(ItemDisplay):
    title = 'Asessment of physical loss'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bPhysicalLossAssesment,
                'MSFD8b_PhysicalLoss',
                self.context.item.MSFD8b_PhysicalLoss_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bPhysicalLossAssesmentIndicator,
            'MSFD8b_PhysicalLoss_Assesment',
            self.item.MSFD8b_PhysicalLoss_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO CHECK IF IMPLEMENTATION IS CORRECT
@register_form_section(A81bPhysicalLosItemDisplay)
class A81bPhysicalLosActivities(ItemDisplay):
    title = 'Activities producing physical loss'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bPhysicalLossActivity,
                sql.MSFD8bPhysicalLossActivityDescription,
                'MSFD8b_PhysicalLoss',
                self.context.item.MSFD8b_PhysicalLoss_ID
            )


@register_form_section(A81bPhysicalLosItemDisplay)
class A81bPhysicalLosImpacts(ItemDisplay):
    title = 'Impacts produced by the physical loss'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bPhysicalLossSumInfo2ImpactedElement,
                'MSFD8b_PhysicalLoss',
                self.context.item.MSFD8b_PhysicalLoss_ID
            )
# endregion Physical loss


# region Pollutant events
class A81bPollutantEventItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bPollutantEvent
    order_field = 'MSFD8b_PollutantEvents_ID'


@register_subform(A81bForm)
class A81bPollutantEventSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Pollutant events'
    mapper_class = sql.MSFD8bPollutantEvent

    def get_subform(self):
        return A81bPollutantEventItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


@register_form_section(A81bPollutantEventItemDisplay)
class A81bPollutantEventAssessment(ItemDisplay):
    title = 'Asessment of pollutant events'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bPollutantEventsAssesment,
                'MSFD8b_PollutantEvents',
                self.context.item.MSFD8b_PollutantEvents_ID
            )

    def get_extra_data(self):
        if not self.item:
            return {}

        count, item = db.get_related_record(
            sql.MSFD8bPollutantEventsAssesmentIndicator,
            'MSFD8b_PollutantEvents_Assesment',
            self.item.MSFD8b_PollutantEvents_Assesment_ID
        )
        # ft = pivot_data(res, 'FeatureType')

        return [
            ('Assesment Indicator', {'Feature': item}),
        ]


#  TODO CHECK IF IMPLEMENTATION IS CORRECT
@register_form_section(A81bPollutantEventItemDisplay)
class A81bPollutantEventActivities(ItemDisplay):
    title = 'Activities producing pollutant events'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bPollutantEventsActivity,
                sql.MSFD8bPollutantEventsActivityDescription,
                'MSFD8b_PollutantEvents',
                self.context.item.MSFD8b_PollutantEvents_ID
            )


@register_form_section(A81bPollutantEventItemDisplay)
class A81bPollutantEventImpacts(ItemDisplay):
    title = 'Impacts produced by the pollutant event'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record(
                sql.MSFD8bPollutantEventsSumInfo2ImpactedElement,
                'MSFD8b_PollutantEvents',
                self.context.item.MSFD8b_PollutantEvents_ID
            )
# endregion Pollutant events


# region Acidification
class A81bAcidificationItemDisplay(MultiItemDisplayForm):
    """ Group the multiple items together for A8.1b
    """
    mapper_class = sql.MSFD8bAcidification
    order_field = 'MSFD8b_Acidification_ID'


@register_subform(A81bForm)
class A81bAcidificationSubForm(MarineUnitIDSelectForm):
    """ Select the MarineUnitID for the Article 8.1b form
    """
    title = 'Acidification'
    mapper_class = sql.MSFD8bAcidification

    def get_subform(self):
        return A81bAcidificationItemDisplay(self, self.request)

    def download_results(self):
        muids = self.get_marine_unit_ids()
        count, data = db.get_all_records(
            self.mapper_class, self.mapper_class.MarineUnitID.in_(muids)
        )

        return data_to_xls(data)


#  TODO CHECK IF IMPLEMENTATION IS CORRECT
@register_form_section(A81bAcidificationItemDisplay)
class A81bAcidificationActivities(ItemDisplay):
    title = 'Activities producing acidification'

    def get_db_results(self):
        if self.context.item:
            return db.get_related_record_join(
                sql.MSFD8bAcidificationActivity,
                sql.MSFD8bAcidificationActivityDescription,
                'MSFD8b_Acidification',
                self.context.item.MSFD8b_Acidification_ID
            )
# endregion Acidification
