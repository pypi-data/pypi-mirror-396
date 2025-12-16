from multiproof import StandardMerkleTree


def generate_merkle_proof_for_claims(claims):
    values = [
        [claim["epoch"], claim["account"], claim["token"], int(claim["cumulativeAmount"])]
        for claim in claims
    ]

    leaf_encoding = ["uint256", "address", "address", "uint256"]

    return generate_merkle_proof(claims, values, leaf_encoding)


def generate_merkle_proof(claims, values, leaf_encoding, total_amount_field="cumulativeAmount"):
    tree = StandardMerkleTree.of(values, leaf_encoding)
    result = {
        "root": tree.root,
        "totalAmount": str(sum(int(claim[total_amount_field]) for claim in claims)),
        "totalClaims": len(values),
        "values": [],
    }

    for claim, value in zip(claims, values, strict=True):
        proof = tree.get_proof(value)
        result["values"].append(
            {
                **claim,
                "proof": list(proof),
            }
        )

    return result
