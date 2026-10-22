SELECT
    member.name AS UserName,
    role.name AS DatabaseRole
FROM sys.database_role_members AS rm
JOIN sys.database_principals AS role
    ON role.principal_id = rm.role_principal_id
JOIN sys.database_principals AS member
    ON member.principal_id = rm.member_principal_id
WHERE member.name IN ('QuynhPham', 'NandaSurendra');