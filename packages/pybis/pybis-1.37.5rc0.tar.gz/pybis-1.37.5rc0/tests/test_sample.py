#   Copyright ETH 2018 - 2024 Zürich, Scientific IT Services
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import datetime
import random
import re
import time
import uuid

import pandas as pd
import pytest


def test_create_delete_sample(space):
    o = space.openbis

    sample_type = "UNKNOWN"
    sample = o.new_sample(
        code="illegal sample name with spaces", type=sample_type, space=space
    )
    with pytest.raises(ValueError):
        sample.save()
        assert "should not have been created" is None

    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    sample_code = "test_sample_" + timestamp + "_" + str(random.randint(0, 1000))
    sample = o.new_sample(code=sample_code, type=sample_type, space=space)
    assert sample is not None
    assert sample.space.code == space.code
    assert sample.code == sample_code
    assert sample.permId == ""
    sample.save()

    # now there should appear a permId
    assert sample.permId is not None

    # get it by permId
    sample_by_permId = o.get_sample(sample.permId)
    assert sample_by_permId is not None

    sample_by_permId = space.get_sample(sample.permId)
    assert sample_by_permId is not None

    assert sample_by_permId.registrator is not None
    assert sample_by_permId.registrationDate is not None
    # check date format: 2019-03-22 11:36:40
    assert (
            re.search(
                r"^\d{4}\-\d{2}\-\d{2} \d{2}\:\d{2}\:\d{2}$",
                sample_by_permId.registrationDate,
            )
            is not None
    )

    # get sample by identifier
    sample_by_identifier = o.get_sample(sample.identifier)
    assert sample_by_identifier is not None

    sample_by_identifier = space.get_sample(sample.identifier)
    assert sample_by_identifier is not None

    sample.delete("sample creation test on " + timestamp)

    with pytest.raises(ValueError):
        o.get_sample(sample.permId)
        assert "This should fail" is None


def test_revert_deletion_sample(space):
    o = space.openbis

    sample_type = "UNKNOWN"
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    sample_code = "test_sample_" + timestamp + "_" + str(random.randint(0, 1000))
    sample = o.new_sample(code=sample_code, type=sample_type, space=space)
    assert sample is not None
    assert sample.space.code == space.code
    assert sample.code == sample_code
    assert sample.permId == ""
    sample.save()

    # now there should appear a permId
    assert sample.permId is not None

    # get it by permId
    sample_by_permId = o.get_sample(sample.permId)
    assert sample_by_permId is not None

    sample_by_permId = space.get_sample(sample.permId)
    assert sample_by_permId is not None

    assert sample_by_permId.registrator is not None
    assert sample_by_permId.registrationDate is not None
    # check date format: 2019-03-22 11:36:40
    assert (
            re.search(
                r"^\d{4}\-\d{2}\-\d{2} \d{2}\:\d{2}\:\d{2}$",
                sample_by_permId.registrationDate,
            )
            is not None
    )

    sample.delete("sample creation test on " + timestamp)

    with pytest.raises(ValueError):
        o.get_sample(sample.permId)
        assert "This should fail" is None

    df = o.get_deletions()
    assert df[df['permId'] == sample.permId].empty is False
    deletionId = df[df['permId'] == sample.permId]['deletionId'].iloc[0]
    o.revert_deletions([deletionId])

    sample = o.get_sample(sample.permId)
    assert sample is not None
    df = o.get_deletions()
    if df.empty is False:
        assert df[df['permId'] == sample.permId].empty is True


def test_create_delete_space_sample(space):
    o = space.openbis
    sample_type = "UNKNOWN"
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    sample_code = "test_sample_" + timestamp + "_" + str(random.randint(0, 1000))

    sample = space.new_sample(code=sample_code, type=sample_type)
    assert sample is not None
    assert sample.space.code == space.code
    assert sample.code == sample_code
    sample.save()
    assert sample.permId is not None
    sample.delete("sample space creation test on " + timestamp)


def test_parent_child(space):
    o = space.openbis
    sample_type = "UNKNOWN"
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    parent_code = (
            "parent_sample_{}".format(timestamp) + "_" + str(random.randint(0, 1000))
    )
    sample_parent = o.new_sample(code=parent_code, type=sample_type, space=space)
    sample_parent.save()

    child_code = "child_sample_{}".format(timestamp)
    sample_child = o.new_sample(
        code=child_code, type=sample_type, space=space, parent=sample_parent
    )
    sample_child.save()
    time.sleep(5)

    ex_sample_parents = sample_child.get_parents()
    ex_sample_parent = ex_sample_parents[0]
    assert (
            ex_sample_parent.identifier == "/{}/{}".format(space.code, parent_code).upper()
    )

    ex_sample_children = ex_sample_parent.get_children()
    ex_sample_child = ex_sample_children[0]
    assert ex_sample_child.identifier == "/{}/{}".format(space.code, child_code).upper()

    sample_parent.delete("sample parent-child creation test on " + timestamp)
    sample_child.delete("sample parent-child creation test on " + timestamp)


def test_empty_data_frame(openbis_instance):
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    sample_type_code = "test_sample_type_" + timestamp + "_" + str(uuid.uuid4())

    sample_type = openbis_instance.new_sample_type(
        code=sample_type_code,
        generatedCodePrefix="S",
        autoGeneratedCode=True,
        subcodeUnique=False,
        listable=True,
        showContainer=False,
        showParents=True,
        showParentMetadata=False
    )
    sample_type.save()

    s = openbis_instance.get_sample_type(sample_type_code)
    pa = s.get_property_assignments()

    attrs = [
        "code",
        "dataType",
        "section",
        "ordinal",
        "mandatory",
        "initialValueForExistingEntities",
        "showInEditView",
        "showRawValueInForms",
        "registrator",
        "registrationDate",
        "plugin"
    ]

    pd.testing.assert_frame_equal(pa.df, pd.DataFrame(columns=attrs))


def test_new_sample_type_with_description(openbis_instance):
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    sample_type_code = "test_sample_type_" + timestamp + "_" + str(uuid.uuid4())

    description = 'my test description'

    sample_type = openbis_instance.new_sample_type(
        code=sample_type_code,
        generatedCodePrefix="S",
        autoGeneratedCode=True,
        subcodeUnique=False,
        listable=True,
        showContainer=False,
        showParents=True,
        showParentMetadata=False,
        description=description
    )
    sample_type.save()

    s = openbis_instance.get_sample_type(sample_type_code)
    assert s.description == description


def test_sample_date_property(space):
    o = space.openbis

    current_date = time.strftime("%Y-%m-%d").lower()

    # Create custom DATE property type
    property_type_code = "test_property_type_" + current_date + "_" + str(uuid.uuid4())
    pt_date = o.new_property_type(
        code=property_type_code,
        label='custom property of data type date',
        description='custom property created in unit test',
        dataType='DATE',
    )
    pt_date.save()

    # Create custom sample type
    sample_type_code = "test_sample_type_" + current_date + "_" + str(uuid.uuid4())
    sample_type = o.new_sample_type(
        code=sample_type_code,
        generatedCodePrefix="S",
        autoGeneratedCode=True,
        listable=True,
    )
    sample_type.save()

    # Assign created property to new sample type
    sample_type.assign_property(
        prop=property_type_code,
        section='',
        ordinal=1,
        mandatory=False,
        showInEditView=True,
        showRawValueInForms=True
    )

    sample_code = "my_sample_{}_{}".format(current_date, str(uuid.uuid4()))
    sample = o.new_sample(code=sample_code,
                          type=sample_type_code,
                          space=space,
                          props={
                              property_type_code: current_date})
    sample.save()

    # New item case
    assert len(sample.props()) == 1
    key, val = sample.props().popitem()
    assert key == property_type_code
    assert val == current_date

    # Update item case
    sample.props = {property_type_code: '2024-05-16'}
    sample.save()

    assert len(sample.props()) == 1
    key, val = sample.props().popitem()
    assert key == property_type_code
    assert val == '2024-05-16'


def test_sample_property_in_isoformat_timestamp(space):
    o = space.openbis

    timestamp = time.strftime("%a_%y%m%d_%H%M%S").lower()

    # Create custom TIMESTAMP property type
    property_type_code = "test_property_type_" + timestamp + "_" + str(uuid.uuid4())
    pt_date = o.new_property_type(
        code=property_type_code,
        label='custom property of data type timestamp',
        description='custom property created in unit test',
        dataType='TIMESTAMP',
    )
    pt_date.save()

    # Create custom sample type
    sample_type_code = "test_sample_type_" + timestamp + "_" + str(uuid.uuid4())
    sample_type = o.new_sample_type(
        code=sample_type_code,
        generatedCodePrefix="S",
        autoGeneratedCode=True,
        listable=True,
    )
    sample_type.save()

    # Assign created property to new sample type
    sample_type.assign_property(
        prop=property_type_code,
        section='',
        ordinal=5,
        mandatory=False,
        showInEditView=True,
        showRawValueInForms=True
    )

    sample_code = "my_sample_{}".format(timestamp)
    # Create new sample with timestamp property in non-supported format
    timestamp_property = datetime.datetime.now().isoformat()
    sample = o.new_sample(code=sample_code,
                          type=sample_type_code,
                          space=space,
                          props={
                              property_type_code: timestamp_property})
    sample.save()

    # New item case
    assert len(sample.props()) == 1
    key, val = sample.props().popitem()
    assert key == property_type_code

    # Update item case
    sample.props = {property_type_code: timestamp_property}
    sample.save()

    assert len(sample.props()) == 1
    key, val = sample.props().popitem()
    assert key == property_type_code

def test_create_sample_type_assign_property(space):
    name_suffix = str(time.time())
    sc = "TEST_" + name_suffix
    pc = "ESFA_" + name_suffix
    ptc1 = "START_DATE_" + name_suffix
    ptc2 = "EXP_DESCRIPTION_" + name_suffix
    stc = "EXPERIMENTAL_STEP_MILAR_" + name_suffix

    # Create the new space and project
    sp = space.openbis.new_space(code=sc, description="Test space")
    sp.save()
    pr = space.openbis.new_project(code=pc, space=sc, description="ESFA experiments")
    pr.save()

    # Create the experiment
    exp = space.openbis.new_collection(code=pc, project="/" + sc + "/" + pc, type="COLLECTION")
    exp.save()

    # Create the sample type
    date_prop = space.openbis.new_property_type(code=ptc1, dataType="TIMESTAMP",
                                                label="Start date",
                                                description="Date of the measurement")
    date_prop.save()
    date_prop = space.openbis.new_property_type(code=ptc2, dataType="MULTILINE_VARCHAR",
                                                label="Experimental description",
                                                description="Experimental description")
    date_prop.save()
    st = space.openbis.new_sample_type(code=stc, generatedCodePrefix="EXSTEPMILAR")
    st.save()

    if st is None:
        print(space.openbis.get_sample_types())
        st = space.openbis.get_sample_type(stc)
        st.save()

    st.assign_property(ptc1)
    st.assign_property(ptc2)
    st.assign_property("$NAME")
    st.save()


def test_del_child_from_sample(space):
    # Prepare
    sample_type = "UNKNOWN"
    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()
    sample_code1 = "test_sample_child_" + timestamp + "_" + str(random.randint(0, 1000))

    sample_child = space.new_sample(code=sample_code1, type=sample_type)
    sample_child.save()

    sample_code2 = "test_sample_parent_" + timestamp + "_" + str(random.randint(0, 1000))
    sample_parent = space.new_sample(code=sample_code2, type=sample_type)
    sample_parent.children = [sample_child]
    sample_parent.save()

    assert sample_parent.children == [sample_child.identifier]

    # Act & Assert
    item = str(sample_parent.children[0])
    sample_parent.del_children(item)
    sample_parent.save()

    assert sample_parent.children == []


def test_sample_with_auto_generated_code(space):
    o = space.openbis

    timestamp = time.strftime("%a_%y%m%d_%H%M%S").lower()

    # Create custom VARCHAR property type
    property_type_code = "test_property_type_" + timestamp + "_" + str(uuid.uuid4())
    pt_date = o.new_property_type(
        code=property_type_code,
        label='custom property of data type varchar',
        description='custom property created in unit test',
        dataType='VARCHAR',
    )
    pt_date.save()

    # Create custom sample type
    sample_type_code = "test_sample_type_" + timestamp + "_" + str(uuid.uuid4())
    sample_type = o.new_sample_type(
        code=sample_type_code,
        generatedCodePrefix="S",
        autoGeneratedCode=True,
        listable=True,
    )
    sample_type.save()

    # Assign created property to new sample type
    sample_type.assign_property(
        prop=property_type_code,
        section='',
        ordinal=5,
        mandatory=False,
        showInEditView=True,
        showRawValueInForms=True
    )

    project = space.new_project(f'my_project_{timestamp}')
    project.save()

    collection = o.new_experiment('UNKNOWN', f'my_collection_{timestamp}', project)
    collection.save()

    sample_code = "my_sample_{}".format(timestamp)
    # create varchar property
    timestamp_property = str(datetime.datetime.now().isoformat())

    sample = space.new_sample(code=sample_code,
                          type=sample_type_code,
                          experiment=collection,
                          props={
                              property_type_code: timestamp_property})
    sample.save()

    assert len(sample.props()) == 1
    key, val = sample.props().popitem()
    assert key == property_type_code
    assert val == timestamp_property


def test_create_sample_clear_property_values(space):
    o = space.openbis

    timestamp = time.strftime("%a_%y%m%d_%H%M%S").lower()

    # Create custom Integer property type
    property_type_code_1 = "test_property_type_" + timestamp + "_" + str(uuid.uuid4())
    pt_integer = o.new_property_type(
        code=property_type_code_1,
        label='custom property of INTEGER type',
        description='custom property created in unit test',
        dataType='INTEGER'
    )
    pt_integer.save()

    property_type_code_2 = "test_property_type_" + timestamp + "_" + str(uuid.uuid4())
    pt_integer_2 = o.new_property_type(
        code=property_type_code_2,
        label='custom property of BOOLEAN type',
        description='custom property created in unit test',
        dataType='BOOLEAN'
    )
    pt_integer_2.save()

    # Create custom sample type
    sample_type_code = "test_sample_type_" + timestamp + "_" + str(uuid.uuid4())
    sample_type = o.new_sample_type(
        code=sample_type_code,
        generatedCodePrefix="S",
        autoGeneratedCode=True,
        listable=True,
    )
    sample_type.save()

    # Assign created property to new sample type
    sample_type.assign_property(
        prop=property_type_code_1,
        section='',
        ordinal=1,
        mandatory=False,
        showInEditView=True,
        showRawValueInForms=True
    )

    sample_type.assign_property(
        prop=property_type_code_2,
        section='',
        ordinal=2,
        mandatory=False,
        showInEditView=True,
        showRawValueInForms=True
    )

    sample_code = "my_sample_{}".format(timestamp)

    # Create new sample with timestamp property in non-supported format
    sample = o.new_sample(code=sample_code,
                          type=sample_type_code,
                          space=space,
                          props={
                              property_type_code_1: 1,
                              property_type_code_2: True,
                                })
    sample.save()

    # New item case
    assert len(sample.props()) == 2
    key, val = sample.props().popitem()
    assert key in [property_type_code_1, property_type_code_2]
    assert val in [1, 'true']
    key, val = sample.props().popitem()
    assert key in [property_type_code_1, property_type_code_2]
    assert val in [1, 'true']

    # Update item case
    sample.props = {property_type_code_1: '', property_type_code_2: None}
    sample.save()

    assert len(sample.props()) == 2
    key, val = sample.props().popitem()
    assert key in [property_type_code_1, property_type_code_2]
    assert val is None
    key, val = sample.props().popitem()
    assert key in [property_type_code_1, property_type_code_2]
    assert val is None

def test_create_sample_with_spreadsheet(space):
    name_suffix = str(time.time())
    sc = "TEST_1_" + name_suffix
    pc = "ESFA_1_" + name_suffix
    ptc1 = "XML_SPREADSHEET_" + name_suffix
    stc = "EXPERIMENTAL_STEP_MILAR_" + name_suffix

    # Create the new space and project
    sp = space.openbis.new_space(code=sc, description="Test space")
    sp.save()
    pr = space.openbis.new_project(code=pc, space=sc, description="ESFA experiments")
    pr.save()

    # Create the experiment
    exp = space.openbis.new_collection(code=pc, project="/" + sc + "/" + pc, type="COLLECTION")
    exp.save()

    # Create the sample type
    date_prop = space.openbis.new_property_type(code=ptc1, dataType="XML",
                                                label="test spreadsheet",
                                                description="test xml property",
                                                metaData={"custom_widget": "Spreadsheet"})
    date_prop.save()

    st = space.openbis.new_sample_type(code=stc, generatedCodePrefix="TEST_PATTERN_")
    st.save()

    if st is None:
        print(space.openbis.get_sample_types())
        st = space.openbis.get_sample_type(stc)
        st.save()

    st.assign_property(ptc1)
    st.save()

    spreadsheet = space.openbis.new_spreadsheet(10, 10)
    spreadsheet.data[0][0] = 10

    sample = space.openbis.new_sample(code=f"CODE_{name_suffix}",
                                      type=st.code,
                                      experiment=exp,
                                      props={ptc1.lower(): spreadsheet})
    sample.save()

    assert sample.props[ptc1.lower()] is not None
    assert sample.props[ptc1.lower()].data[0][0] == 10

def test_parent_child_in_project(space):
    o = space.openbis

    timestamp = time.strftime("%a_%y%m%d_%H%M%S").upper()

    project = space.new_project(f'my_project_{timestamp}')
    project.save()

    collection = o.new_experiment('UNKNOWN', f'my_collection_{timestamp}', project)
    collection.save()

    sample_type = "UNKNOWN"

    parent_code = (
            "parent_sample_{}".format(timestamp) + "_" + str(random.randint(0, 1000))
    )
    sample_parent = o.new_sample(code=parent_code, type=sample_type, collection=collection)
    sample_parent.save()

    child_code = "child_sample_{}".format(timestamp)
    sample_child = o.new_sample(
        code=child_code, type=sample_type, collection=collection, parent=sample_parent
    )
    sample_child.save()
    time.sleep(5)

    samples = o.get_samples(sample_parent)
    assert len(samples) == 1
    assert samples[0].children == '--NOT FETCHED--'
    child = samples[0].get_children()
    assert child is not None
    assert len(child) == 1
    assert samples[0].children[0] == sample_child.identifier
    children = samples.get_children()
    assert children is not None
    assert len(children) == 1
    assert samples[0].get_children().get_parents()[0].identifier == samples[0].identifier
