# LittleOrange::Organizations::OrganizationalUnit

Resource schema for AWS Organizations Organizational Unit resource

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "LittleOrange::Organizations::OrganizationalUnit",
    "Properties" : {
        "<a href="#parentid" title="ParentId">ParentId</a>" : <i>String</i>,
        "<a href="#name" title="Name">Name</a>" : <i>String</i>
    }
}
</pre>

### YAML

<pre>
Type: LittleOrange::Organizations::OrganizationalUnit
Properties:
    <a href="#parentid" title="ParentId">ParentId</a>: <i>String</i>
    <a href="#name" title="Name">Name</a>: <i>String</i>
</pre>

## Properties

#### ParentId

The unique identifier (ID) of the parent root or OU that this OU resides in (Root ID or OU ID allowed)

_Required_: Yes

_Type_: String

_Pattern_: <code>^(ou-[a-z0-9]{4,32}-[a-z0-9]{8,32}|r-[a-z0-9]{4,32})$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### Name

The friendly name of this Organizational Unit (OU)

_Required_: Yes

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the Id.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### Arn

The ARN of this Organizational Unit (OU).

#### Id

The unique identifier (ID) of this Organizational Unit (OU).

